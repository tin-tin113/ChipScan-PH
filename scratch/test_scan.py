import os
import django
import cv2
import numpy as np

import sys
sys.path.append('.')

# Configure django settings first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chipscan_project.settings')
django.setup()

from scanner.ocr_pipeline import load_image, preprocess_image, get_ocr_engine, traverse_ocr_results

def test_ocr_flow():
    print("Creating mock chip image...")
    # Create a simple BGR image with text
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    img.fill(40) # Dark gray background
    
    # Write some clear text mimicking chip laser etch
    cv2.putText(img, "SAMSUNG", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (220, 220, 220), 3)
    cv2.putText(img, "KLUEG8UHDB", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (220, 220, 220), 3)
    cv2.putText(img, "C2D1", (300, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (220, 220, 220), 3)
    
    # Save mock image
    temp_path = "mock_chip_test.png"
    cv2.imwrite(temp_path, img)
    print(f"Mock image saved to {temp_path}")
    
    try:
        print("Running image preprocessing...")
        processed = preprocess_image(img)
        temp_pre_path = "mock_chip_preprocessed.png"
        cv2.imwrite(temp_pre_path, processed)
        print(f"Preprocessed image saved to {temp_pre_path}")
        
        print("Initializing PaddleOCR...")
        import paddle
        paddle.set_flags({
            "FLAGS_fraction_of_cpu_memory_to_use": 0.1,
            "FLAGS_allocator_strategy": "naive_best_fit",
            "FLAGS_eager_delete_scope": True,
            "FLAGS_eager_delete_tensor_gb": 0.0,
            "FLAGS_fast_eager_deletion_mode": True,
            "FLAGS_use_pinned_memory": False
        })
        
        # Temporarily re-initialize get_ocr_engine settings for testing
        from scanner import ocr_pipeline
        ocr_pipeline._ocr_engine = None # Force re-init
        
        # Let's override ocr_pipeline's get_ocr_engine to use PP-OCRv4
        original_get = ocr_pipeline.get_ocr_engine
        def get_v4_engine():
            import os
            os.environ['FLAGS_use_onednn'] = '0'
            os.environ['CPU_NUM'] = '1'
            os.environ['OMP_NUM_THREADS'] = '1'
            os.environ['MKL_NUM_THREADS'] = '1'
            from paddleocr import PaddleOCR
            import logging
            logging.getLogger("ppocr").setLevel(logging.ERROR)
            return PaddleOCR(
                ocr_version='PP-OCRv4',
                use_textline_orientation=False,
                lang='en',
                enable_mkldnn=False,
                use_doc_unwarping=False,
                use_doc_orientation_classify=False
            )
        ocr_pipeline.get_ocr_engine = get_v4_engine
        
        ocr = ocr_pipeline.get_ocr_engine()
        
        print("Executing OCR text recognition...")
        results = ocr.ocr(temp_pre_path)
        
        print("OCR raw results:")
        print(results)
        
        tokens = traverse_ocr_results(results)
        print("Extracted tokens:")
        print(tokens)
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
    finally:
        # Clean up files
        for p in [temp_path, temp_pre_path]:
            if os.path.exists(p):
                os.remove(p)
                print(f"Cleaned up {p}")

if __name__ == "__main__":
    test_ocr_flow()
