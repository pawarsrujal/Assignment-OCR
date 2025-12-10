"""Unit tests for OCR module."""

import pytest
import numpy as np
import cv2
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.ocr import ocr_tesseract, ocr_easyocr, ensemble_ocr


@pytest.fixture
def sample_text_image():
    """Create a simple image with text for OCR testing."""
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Hello World', (50, 100), font, 2, (0, 0, 0), 3)
    return img


def test_ocr_tesseract_returns_list(sample_text_image):
    """Test ocr_tesseract returns a list."""
    result = ocr_tesseract(sample_text_image, conf_threshold=0)
    assert isinstance(result, list)


def test_ocr_tesseract_result_structure(sample_text_image):
    """Test ocr_tesseract results have expected keys."""
    result = ocr_tesseract(sample_text_image, conf_threshold=0)
    if result:
        for item in result:
            assert 'text' in item
            assert 'confidence' in item
            assert 'bbox' in item
            assert len(item['bbox']) == 4


def test_ocr_easyocr_returns_list(sample_text_image):
    """Test ocr_easyocr returns a list."""
    result = ocr_easyocr(sample_text_image, conf_threshold=0.0)
    assert isinstance(result, list)


def test_ocr_easyocr_result_structure(sample_text_image):
    """Test ocr_easyocr results have expected keys."""
    result = ocr_easyocr(sample_text_image, conf_threshold=0.0)
    if result:
        for item in result:
            assert 'text' in item
            assert 'confidence' in item
            assert 'bbox' in item
            assert len(item['bbox']) == 4


def test_ensemble_ocr_returns_list(sample_text_image):
    """Test ensemble_ocr returns a list."""
    result = ensemble_ocr(sample_text_image, conf_threshold=0.0)
    assert isinstance(result, list)


def test_ensemble_ocr_result_structure(sample_text_image):
    """Test ensemble_ocr results have expected keys and types."""
    result = ensemble_ocr(sample_text_image, conf_threshold=0.0)
    if result:
        for item in result:
            assert 'text' in item
            assert 'confidence' in item
            assert 'bbox' in item
            assert 'source' in item
            assert isinstance(item['confidence'], (int, float))
            assert 0.0 <= item['confidence'] <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
