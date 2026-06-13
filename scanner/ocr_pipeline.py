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
        from paddleocr import PaddleOCR
        import logging
        logging.getLogger("ppocr").setLevel(logging.ERROR)
        _ocr_engine = PaddleOCR(
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
    Runs the image through the pipeline:
    Grayscale -> Resize (min 800px Lanczos) -> Deskew -> Bilateral -> CLAHE -> Median Blur -> Sharpen.
    """
    # 1. Convert to grayscale
    if len(cv_image.shape) == 3:
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv_image.copy()

    # 2. Smart Resizing: Keep size bounded to speed up inference while maintaining OCR quality
    h, w = gray.shape[:2]
    max_side = 800
    if max(h, w) > max_side:
        # Scale down large images using Area interpolation (best for downscaling)
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

    # 4. Bilateral filter to remove screen moire/grid noise while preserving edges
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)

    # 5. CLAHE contrast adjustment
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(bilateral)

    # 6. Median blur
    m_blur = cv2.medianBlur(contrast, 3)

    # 7. Sharpening using Gaussian unsharp mask
    blurred = cv2.GaussianBlur(m_blur, (5, 5), 0)
    sharpened = cv2.addWeighted(m_blur, 1.5, blurred, -0.5, 0)

    return sharpened

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
