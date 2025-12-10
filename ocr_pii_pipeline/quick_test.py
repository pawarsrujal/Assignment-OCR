"""Quick test script to verify pipeline functionality."""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.preprocess import load_image, preprocess_full_pipeline
from pipeline.ocr import ensemble_ocr, ocr_tesseract, ocr_easyocr
from pipeline.pii import extract_pii_from_ocr, detect_regex_pii
from pipeline.redact import redact_image
from pipeline.utils import save_json, save_image, ensure_dir


def test_preprocessing():
    """Test image preprocessing."""
    print("\n" + "="*60)
    print("Test 1: Image Preprocessing")
    print("="*60)
    
    # Create a test image
    img = np.ones((200, 400, 3), dtype=np.uint8) * 200
    cv2.putText(img, 'Test Image', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Preprocess
    try:
        preprocessed = preprocess_full_pipeline(img, upscale=False)
        print(f"✓ Preprocessing successful")
        print(f"  Input shape: {img.shape}")
        print(f"  Output shape: {preprocessed.shape}")
        return True
    except Exception as e:
        print(f"✗ Preprocessing failed: {e}")
        return False


def test_pii_detection():
    """Test PII regex detection."""
    print("\n" + "="*60)
    print("Test 2: PII Detection (Regex)")
    print("="*60)
    
    test_text = """
    Contact Information:
    Email: john.doe@example.com
    Phone: +1-555-123-4567
    Date: 15/12/2023
    AADHAR: 1234 5678 9012
    """
    
    try:
        pii_items = detect_regex_pii(test_text)
        print(f"✓ PII detection successful")
        print(f"  Detected {len(pii_items)} PII items:")
        for pii_type, text, span in pii_items:
            print(f"    - {pii_type}: {text}")
        return len(pii_items) > 0
    except Exception as e:
        print(f"✗ PII detection failed: {e}")
        return False


def test_ocr_simple():
    """Test OCR on a simple generated image."""
    print("\n" + "="*60)
    print("Test 3: OCR (Simple Text)")
    print("="*60)
    
    # Create image with clear text
    img = np.ones((150, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'Hello World', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    try:
        # Test Tesseract
        results = ocr_tesseract(img, conf_threshold=0)
        print(f"✓ Tesseract OCR successful")
        print(f"  Detected {len(results)} text regions")
        if results:
            print(f"  Sample: '{results[0]['text']}' (conf: {results[0]['confidence']:.2f})")
        
        return True
    except Exception as e:
        print(f"✗ OCR failed: {e}")
        print(f"  Note: Make sure Tesseract is installed and in PATH")
        return False


def test_redaction():
    """Test image redaction."""
    print("\n" + "="*60)
    print("Test 4: Image Redaction")
    print("="*60)
    
    # Create test image
    img = np.ones((200, 400, 3), dtype=np.uint8) * 200
    
    # Mock PII items
    pii_items = [
        {'type': 'email', 'bbox': [50, 50, 100, 30], 'confidence': 0.9}
    ]
    
    try:
        redacted = redact_image(img, pii_items, method='black')
        print(f"✓ Redaction successful")
        print(f"  Redacted {len(pii_items)} regions")
        return True
    except Exception as e:
        print(f"✗ Redaction failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OCR PII Pipeline - Quick Test Suite")
    print("="*60)
    
    results = []
    results.append(("Preprocessing", test_preprocessing()))
    results.append(("PII Detection", test_pii_detection()))
    results.append(("OCR", test_ocr_simple()))
    results.append(("Redaction", test_redaction()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Pipeline is ready to use.")
        print("\nRun the full pipeline with:")
        print("  python run_pipeline.py --input examples/ --output out/ --redact")
    else:
        print("\n⚠ Some tests failed. Please check installation:")
        print("  - Run: python setup.py")
        print("  - Verify Tesseract is installed: tesseract --version")
        print("  - Install dependencies: pip install -r requirements.txt")
    
    print()
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
