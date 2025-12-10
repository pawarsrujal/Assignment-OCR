"""Unit tests for preprocessing module."""

import pytest
import numpy as np
import cv2
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.preprocess import (
    load_image, deskew_image, enhance_image, binarize_image, upscale_image
)


@pytest.fixture
def sample_image():
    """Create a simple test image (solid color)."""
    img = np.ones((100, 100, 3), dtype=np.uint8) * 200
    return img


@pytest.fixture
def sample_gray():
    """Create a simple grayscale test image."""
    gray = np.ones((100, 100), dtype=np.uint8) * 150
    return gray


def test_deskew_image(sample_gray):
    """Test deskew function preserves image shape."""
    result = deskew_image(sample_gray)
    assert result.shape == sample_gray.shape
    assert result.dtype == sample_gray.dtype


def test_enhance_image(sample_image):
    """Test enhance function returns valid grayscale output."""
    result = enhance_image(sample_image)
    assert result.ndim == 2  # Grayscale
    assert result.shape[:2] == sample_image.shape[:2]
    assert result.dtype == np.uint8


def test_binarize_image(sample_gray):
    """Test binarize function returns binary (0, 255) values."""
    result = binarize_image(sample_gray)
    assert result.shape == sample_gray.shape
    # Check that result contains only 0 and 255
    unique_vals = np.unique(result)
    assert all(v in [0, 255] for v in unique_vals)


def test_upscale_image(sample_image):
    """Test upscale function increases image dimensions."""
    scale_factor = 2.0
    result = upscale_image(sample_image, scale_factor)
    expected_h = int(sample_image.shape[0] * scale_factor)
    expected_w = int(sample_image.shape[1] * scale_factor)
    assert result.shape[0] == expected_h
    assert result.shape[1] == expected_w


def test_load_image_nonexistent():
    """Test load_image raises error for nonexistent file."""
    with pytest.raises(RuntimeError):
        load_image("/nonexistent/path/image.jpg")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
