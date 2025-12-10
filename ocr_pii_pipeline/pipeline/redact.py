"""Image redaction: black box, blur, and utility functions."""

import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional


def redact_image(img_bgr: np.ndarray, pii_list: List[Dict], method: str = 'black') -> np.ndarray:
    """
    Redact PII regions in image using specified method.
    method: 'black' (fill with black box), 'blur' (Gaussian blur).
    """
    redacted = img_bgr.copy()
    
    for pii_item in pii_list:
        bbox = pii_item.get('bbox')
        if not bbox or all(v == 0 for v in bbox):
            continue
        
        x, y, w, h = bbox
        # Convert to integers for array slicing
        x = int(max(0, x))
        y = int(max(0, y))
        w = int(w)
        h = int(h)
        x_end = int(min(x + w, img_bgr.shape[1]))
        y_end = int(min(y + h, img_bgr.shape[0]))
        
        if x >= x_end or y >= y_end or w <= 0 or h <= 0:
            continue
        
        if method == 'black':
            # Fill with black
            redacted[y:y_end, x:x_end] = 0
        elif method == 'blur':
            # Apply Gaussian blur
            roi = redacted[y:y_end, x:x_end]
            blurred = cv2.GaussianBlur(roi, (15, 15), 0)
            redacted[y:y_end, x:x_end] = blurred
    
    return redacted


def save_json(obj: Dict, path: str) -> None:
    """Save dictionary to JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> Dict:
    """Load JSON from file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_image(img: np.ndarray, path: str) -> None:
    """Save image to file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)


def bbox_to_tuple(bbox: List[int]) -> Tuple[int, int, int, int]:
    """Convert bbox [x, y, w, h] to tuple."""
    return tuple(bbox) if len(bbox) == 4 else (0, 0, 0, 0)


def draw_boxes(img: np.ndarray, boxes: List[Dict], color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
    """Draw bounding boxes on image for visualization."""
    result = img.copy()
    for box_info in boxes:
        bbox = box_info.get('bbox', [0, 0, 0, 0])
        if all(v == 0 for v in bbox):
            continue
        x, y, w, h = bbox
        x_end = min(x + w, img.shape[1])
        y_end = min(y + h, img.shape[0])
        x = max(0, x)
        y = max(0, y)
        cv2.rectangle(result, (x, y), (x_end, y_end), color, thickness)
        
        # Optional: add label
        label = f"{box_info.get('type', 'PII')} ({box_info.get('confidence', 0):.2f})"
        cv2.putText(result, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result


def ensure_dir(path: str) -> None:
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)
