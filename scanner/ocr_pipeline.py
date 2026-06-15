import os
import re
import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener
from difflib import SequenceMatcher

# Register HEIF opener for iOS uploads support
register_heif_opener()

_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        # Disable oneDNN to avoid new PIR executor conversion crash on CPU
        os.environ['FLAGS_use_onednn'] = '0'
        # Limit CPU threads to reduce memory footprint on limited hosting (Render free tier)
        os.environ['CPU_NUM'] = '1'
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
        os.environ['NUMEXPR_NUM_THREADS'] = '1'
        
        # Configure PaddlePaddle memory flags
        import paddle
        paddle.set_flags({
            "FLAGS_fraction_of_cpu_memory_to_use": 0.1,
            "FLAGS_allocator_strategy": "naive_best_fit",
            "FLAGS_eager_delete_scope": True,
            "FLAGS_eager_delete_tensor_gb": 0.0,
            "FLAGS_fast_eager_deletion_mode": True,
            "FLAGS_use_pinned_memory": False
        })
        
        from paddleocr import PaddleOCR
        import logging
        logging.getLogger("ppocr").setLevel(logging.ERROR)
        _ocr_engine = PaddleOCR(
            ocr_version='PP-OCRv4',
            use_textline_orientation=False,
            lang='en',
            enable_mkldnn=False,
            use_doc_unwarping=False,
            use_doc_orientation_classify=False
        )
    return _ocr_engine

def load_image(image_path_or_file):
    """
    Loads an image safely using Pillow to support format variations (HEIC, etc.) 
    and returns a standard OpenCV BGR image.
    """
    try:
        pil_img = Image.open(image_path_or_file)
        rgb_img = pil_img.convert('RGB')
        img = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        if isinstance(image_path_or_file, str):
            return cv2.imread(image_path_or_file)
        raise e

def deskew(gray):
    """
    Straighten the text rotation using Hough lines to detect the dominant angle.
    """
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    angles = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if -45 < angle < 45:
                angles.append(angle)
    
    if len(angles) > 0:
        median_angle = np.median(angles)
        if abs(median_angle) > 0.5:
            h, w = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated, median_angle
    return gray, 0.0

def preprocess_image(cv_image):
    """
    Runs the image through the optimized pipeline:
    Grayscale -> Resize (max 1600px, Area interpolation) -> Deskew ->
    Gaussian Blur (5x5) -> Otsu Binarization.

    This pipeline was chosen over the previous Bilateral+CLAHE+Median+Sharpen stack
    because CLAHE amplified screen moire/scanline noise and the 800px resize limit
    eroded thin laser-etched characters, both causing OCR failures on real-world chip scans.
    Gaussian Blur smooths out sensor grid noise while Otsu Binarization maximizes
    contrast between text and chip surface regardless of lighting conditions.
    """
    # 1. Convert to grayscale
    if len(cv_image.shape) == 3:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_image.copy()

    # 2. Smart Resizing: Scale up to 1600px max side to preserve fine character detail.
    #    Area interpolation is best for downscaling; Lanczos4 is best for upscaling.
    h, w = gray.shape[:2]
    max_side = 1600
    if max(h, w) > max_side:
        scale = max_side / float(max(h, w))
        new_w = int(round(w * scale))
        new_h = int(round(h * scale))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
    elif min(h, w) < 300:
        # Scale up very small images using Lanczos interpolation
        scale = 300 / float(min(h, w))
        new_w = int(round(w * scale))
        new_h = int(round(h * scale))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # 3. Deskewing (rotate to align text horizontally)
    gray, angle = deskew(gray)

    # 4. Gaussian Blur (5x5) to remove high-frequency sensor grid / moire noise
    #    while keeping character edges intact for binarization.
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 5. Otsu Binarization: automatically picks the optimal threshold to
    #    cleanly separate dark laser-etched text from bright chip surface.
    _, binarized = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binarized

def compute_phash(cv_image):
    """
    Computes a 32-character hex DCT-based perceptual hash (pHash) (128 bits).
    """
    if cv_image is None:
        return ""
    
    if len(cv_image.shape) == 3:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_image
        
    # 1. Resize to 32x32
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    
    # 2. Compute 2D Discrete Cosine Transform (DCT)
    dct = cv2.dct(np.float32(resized))
    
    # 3. Extract top-left 16x8 coefficients to get 128 coefficients (128 bits)
    dct_low = dct[0:16, 0:8]
    
    # 4. Flatten and find the median (exclude DC term at index 0 to remain brightness-invariant)
    flat = dct_low.flatten()
    median = np.median(flat[1:])
    
    # 5. Build 128-bit binary string
    hash_bits = "".join(['1' if val > median else '0' for val in flat])
    
    # 6. Convert to 32-character hex representation
    hash_hex = f"{int(hash_bits, 2):032x}"
    return hash_hex

def hamming_distance(hash1, hash2):
    """
    Calculates the Hamming distance between two 32-character hex hashes (128 bits).
    """
    if not hash1 or not hash2 or len(hash1) != len(hash2):
        return 999
    try:
        h1_val = int(hash1, 16)
        h2_val = int(hash2, 16)
        xor_val = h1_val ^ h2_val
        return bin(xor_val).count('1')
    except ValueError:
        return 999

def traverse_ocr_results(data):
    """
    Recursively flattens PaddleOCR output list or dict structure to extract list of (text, confidence).
    """
    tokens = []
    if isinstance(data, list):
        for item in data:
            tokens.extend(traverse_ocr_results(item))
    elif isinstance(data, dict):
        if 'rec_texts' in data and 'rec_scores' in data:
            for text, score in zip(data['rec_texts'], data['rec_scores']):
                tokens.append((text, score))
        else:
            for val in data.values():
                tokens.extend(traverse_ocr_results(val))
    elif isinstance(data, tuple) and len(data) == 2 and isinstance(data[0], str) and isinstance(data[1], (float, int)):
        tokens.append(data)
    return tokens

def normalize_text(text):
    if not text:
        return ""
    return re.sub(r'[^A-Z0-9]', '', text.upper())

def normalize_and_split(text):
    if not text:
        return []
    parts = re.split(r'[,;\s]+', text)
    return [normalize_text(p) for p in parts if normalize_text(p)]

def get_similarity_ratio(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

def compute_match_score(extracted_normalized, chip):
    """
    Scores a candidate chip against normalized text using string matches, similarity, and prefix weights.
    """
    code_norm = normalize_text(chip.code)
    aliases_norm = normalize_and_split(chip.alias)
    alts_norm = normalize_and_split(chip.alternate_codes)
    
    targets = [code_norm] + aliases_norm + alts_norm
    best_score = 0.0
    
    for target in targets:
        if not target:
            continue
        
        # Substring exact matches (only allow if target is in the extracted text,
        # or if the extracted token is long enough to avoid random character noise)
        if target in extracted_normalized:
            score = 0.85 + (len(target) / len(extracted_normalized)) * 0.15
            best_score = max(best_score, score)
        elif len(extracted_normalized) >= 4 and extracted_normalized in target:
            score = 0.70 + (len(extracted_normalized) / len(target)) * 0.20
            best_score = max(best_score, score)
            
        # Similarity score
        sim = get_similarity_ratio(extracted_normalized, target)
        best_score = max(best_score, sim)
        
        # Check manufacturer prefix match
        if len(extracted_normalized) >= 3:
            prefixes = ('KM', 'KLM', 'KLU', 'TH', 'H9', 'MT', 'SDIN', 'HN', 'TY')
            for prefix in prefixes:
                if extracted_normalized.startswith(prefix) and target.startswith(prefix):
                    best_score = max(best_score, sim + 0.05)
                    break
                
    return min(best_score, 1.0)

def match_chip_heuristics(tokens):
    """
    Queries all chips and finds the best match based on extracted tokens.
    """
    from scanner.models import Chip
    
    if not tokens:
        return None, 0.0
        
    all_ocr_text = " ".join([t[0] for t in tokens])
    extracted_normalized = normalize_text(all_ocr_text)
    token_norms = [normalize_text(t[0]) for t in tokens if normalize_text(t[0])]
    
    best_chip = None
    best_score = 0.0
    
    chips = Chip.objects.all()
    for chip in chips:
        # Score against the full combined string
        score = compute_match_score(extracted_normalized, chip)
        
        # Score against individual tokens
        for tok in token_norms:
            tok_score = compute_match_score(tok, chip)
            if tok_score > score:
                score = tok_score
                
        if score > best_score:
            best_score = score
            best_chip = chip
            
    return best_chip, best_score
