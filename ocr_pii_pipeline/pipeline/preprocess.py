"""Image preprocessing: deskew, denoise, enhance contrast, binarize."""

import cv2
import numpy as np
from typing import Tuple, Optional


def load_image(path: str) -> np.ndarray:
    """Load image from file path; return BGR array. Raises exception on corrupt files."""
    try:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Failed to load image: {path}")
        return img
    except Exception as e:
        raise RuntimeError(f"Error loading image {path}: {str(e)}")


def deskew_image(gray: np.ndarray) -> np.ndarray:
    """Estimate and correct skew in grayscale image using Hough transform."""
    h, w = gray.shape
    edges = cv2.Canny(gray, 100, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=w // 2, maxLineGap=20)
    
    if lines is None or len(lines) == 0:
        return gray
    
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)
    
    median_angle = np.median(angles)
    if abs(median_angle) < 1:
        return gray
    
    # Rotate to correct skew
    center = (w // 2, h // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(gray, rot_matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return rotated


def enhance_image(bgr: np.ndarray) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization), bilateral filter, morphology."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE with higher clip limit for handwritten text
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Bilateral filter to reduce noise while preserving edges
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Sharpen to enhance handwritten text edges
    kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel_sharpen)
    
    # Morphological operations: opening to remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    opened = cv2.morphologyEx(sharpened, cv2.MORPH_OPEN, kernel)
    
    return opened


def binarize_image(gray: np.ndarray) -> np.ndarray:
    """Convert grayscale to binary using Otsu's thresholding."""
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def upscale_image(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    """Upscale image to improve OCR on small text."""
    h, w = image.shape[:2]
    new_h, new_w = int(h * scale), int(w * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


def preprocess_full_pipeline(bgr: np.ndarray, upscale: bool = False, scale_factor: float = 2.0) -> np.ndarray:
    """Complete preprocessing pipeline: deskew → enhance → optionally upscale."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    deskewed = deskew_image(gray)
    enhanced = enhance_image(cv2.cvtColor(deskewed, cv2.COLOR_GRAY2BGR))
    
    if upscale:
        enhanced = upscale_image(enhanced, scale_factor)
    
    return enhanced
