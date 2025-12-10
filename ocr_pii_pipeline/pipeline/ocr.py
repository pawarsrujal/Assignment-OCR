"""OCR wrappers: Tesseract, EasyOCR, and ensemble merge with deduplication."""

import cv2
import numpy as np
import pytesseract
import easyocr
from typing import List, Dict, Optional
from rapidfuzz import fuzz


# Global EasyOCR reader (cached for efficiency)
_easyocr_reader = None


def get_easyocr_reader(lang: str = 'en'):
    """Lazy-load EasyOCR reader to avoid redundant initialization."""
    global _easyocr_reader
    if _easyocr_reader is None:
        _easyocr_reader = easyocr.Reader([lang], gpu=False)
    return _easyocr_reader


def ocr_tesseract(bgr: np.ndarray, conf_threshold: int = 30) -> List[Dict]:
    """Extract text using Tesseract. Returns list of {text, conf, bbox}."""
    pil_img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    from PIL import Image
    pil_img = Image.fromarray(pil_img)
    
    try:
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
        results = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            if conf >= conf_threshold and text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                results.append({
                    'text': text,
                    'confidence': conf / 100.0,  # Normalize to 0-1
                    'bbox': [x, y, w, h]  # [x, y, width, height]
                })
        return results
    except Exception as e:
        print(f"Tesseract OCR error: {e}")
        return []


def ocr_easyocr(bgr: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
    """Extract text using EasyOCR. Returns list of {text, conf, bbox}."""
    try:
        reader = get_easyocr_reader()
        # Enhanced parameters for handwritten text: lower width_ths, allow more detail, lower threshold
        results_easyocr = reader.readtext(bgr, detail=1, paragraph=False, 
                                          width_ths=0.4, height_ths=0.5,
                                          decoder='beamsearch', beamWidth=5,
                                          min_size=10, text_threshold=0.6, 
                                          low_text=0.3, link_threshold=0.3)
        
        results = []
        for detection in results_easyocr:
            bbox_points, text, conf = detection
            if conf >= conf_threshold and text.strip():
                # bbox_points is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [p[0] for p in bbox_points]
                y_coords = [p[1] for p in bbox_points]
                x, y = min(x_coords), min(y_coords)
                w = max(x_coords) - x
                h = max(y_coords) - y
                results.append({
                    'text': text.strip(),
                    'confidence': conf,
                    'bbox': [x, y, w, h]
                })
        return results
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return []


def _fuzzy_match_text(text1: str, text2: str, threshold: float = 0.8) -> bool:
    """Check if two texts are similar using fuzzy matching."""
    return fuzz.ratio(text1.lower(), text2.lower()) / 100.0 >= threshold


def _bbox_overlap(bbox1: List[int], bbox2: List[int], threshold: float = 0.5) -> bool:
    """Check if two bounding boxes overlap significantly."""
    x1_min, y1_min, w1, h1 = bbox1
    x2_min, y2_min, w2, h2 = bbox2
    
    x1_max = x1_min + w1
    y1_max = y1_min + h1
    x2_max = x2_min + w2
    y2_max = y2_min + h2
    
    # Calculate intersection
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_min >= inter_x_max or inter_y_min >= inter_y_max:
        return False
    
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = w1 * h1
    box2_area = w2 * h2
    
    union_area = box1_area + box2_area - inter_area
    iou = inter_area / union_area if union_area > 0 else 0
    
    return iou >= threshold


def ensemble_ocr(
    bgr: np.ndarray,
    weights: Optional[Dict[str, float]] = None,
    conf_threshold: float = 0.25
) -> List[Dict]:
    """
    Ensemble OCR: merge Tesseract and EasyOCR results, deduplicate by fuzzy-match and bbox overlap.
    Returns combined list with normalized confidence scores weighted by engine.
    """
    if weights is None:
        weights = {'easyocr': 0.7, 'tesseract': 0.3}
    
    tesseract_results = ocr_tesseract(bgr, conf_threshold=int(conf_threshold * 100))
    easyocr_results = ocr_easyocr(bgr, conf_threshold=conf_threshold)
    
    # Tag results with source
    for r in tesseract_results:
        r['source'] = 'tesseract'
    for r in easyocr_results:
        r['source'] = 'easyocr'
    
    # Start with EasyOCR results
    merged = []
    used_easy = set()
    
    for easy_idx, easy_result in enumerate(easyocr_results):
        merged_with = False
        for tess_idx, tess_result in enumerate(tesseract_results):
            # Check if texts match (fuzzy) and boxes overlap
            if (_fuzzy_match_text(easy_result['text'], tess_result['text'], threshold=0.75) and
                _bbox_overlap(easy_result['bbox'], tess_result['bbox'], threshold=0.4)):
                # Merge: use higher confidence, average bbox
                merged_result = {
                    'text': easy_result['text'],
                    'confidence': max(
                        easy_result['confidence'] * weights['easyocr'],
                        tess_result['confidence'] * weights['tesseract']
                    ),
                    'bbox': [
                        int((easy_result['bbox'][0] + tess_result['bbox'][0]) / 2),
                        int((easy_result['bbox'][1] + tess_result['bbox'][1]) / 2),
                        int((easy_result['bbox'][2] + tess_result['bbox'][2]) / 2),
                        int((easy_result['bbox'][3] + tess_result['bbox'][3]) / 2)
                    ],
                    'source': 'ensemble'
                }
                merged.append(merged_result)
                used_easy.add(easy_idx)
                merged_with = True
                break
        
        if not merged_with:
            # Add unmatched EasyOCR result
            merged_result = easy_result.copy()
            merged_result['confidence'] *= weights['easyocr']
            merged.append(merged_result)
            used_easy.add(easy_idx)
    
    # Add unmatched Tesseract results
    for tess_idx, tess_result in enumerate(tesseract_results):
        is_duplicate = False
        for easy_idx in used_easy:
            if (tess_idx < len(easyocr_results) and
                _fuzzy_match_text(tess_result['text'], easyocr_results[easy_idx]['text'], threshold=0.75)):
                is_duplicate = True
                break
        if not is_duplicate:
            merged_result = tess_result.copy()
            merged_result['confidence'] *= weights['tesseract']
            merged.append(merged_result)
    
    return merged
