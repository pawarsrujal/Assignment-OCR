"""Utility functions: helpers for common operations."""

import cv2
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def save_json(obj: Dict, path: str) -> None:
    """Save dictionary to JSON file with pretty formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)


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


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + 'Z'


def summarize_pii_counts(pii_list: List[Dict]) -> Dict[str, int]:
    """Count PII items by type."""
    counts = {}
    for pii in pii_list:
        pii_type = pii.get('type', 'unknown')
        counts[pii_type] = counts.get(pii_type, 0) + 1
    return counts
