"""PII extraction: regex patterns + spaCy NER + heuristics."""

import re
from typing import List, Tuple, Dict, Optional
import spacy


# Lazy-load spaCy model
_nlp_model = None


def get_nlp_model():
    """Lazy-load spaCy English model."""
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model 'en_core_web_sm' not found. Install with:")
            print("  python -m spacy download en_core_web_sm")
            _nlp_model = None
    return _nlp_model


def clean_text(s: str) -> str:
    """Normalize whitespace and punctuation."""
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def detect_regex_pii(text: str) -> List[Tuple[str, str, Tuple[int, int]]]:
    """
    Extract PII using regex patterns.
    Returns list of (type, matched_text, (start_pos, end_pos)).
    """
    pii_list = []
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for match in re.finditer(email_pattern, text):
        pii_list.append(('email', match.group(), match.span()))
    
    # Phone pattern: various formats (+XX XXXXXXX, (XXX) XXX-XXXX, XXX-XXX-XXXX, XXXXXXXXXX, etc.)
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b'
    for match in re.finditer(phone_pattern, text):
        pii_list.append(('phone', match.group(), match.span()))
    
    # Date patterns (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    for match in re.finditer(date_pattern, text):
        pii_list.append(('date', match.group(), match.span()))
    
    # AADHAR-like pattern: 12 digits with optional spaces/hyphens
    aadhar_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    for match in re.finditer(aadhar_pattern, text):
        pii_list.append(('aadhar', match.group(), match.span()))
    
    # Credit card-like pattern: 16 digits
    cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    for match in re.finditer(cc_pattern, text):
        # Avoid double-counting as AADHAR
        if match.group() not in [item[1] for item in pii_list if item[0] == 'aadhar']:
            pii_list.append(('credit_card', match.group(), match.span()))
    
    # Social Security Number-like pattern: XXX-XX-XXXX
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    for match in re.finditer(ssn_pattern, text):
        pii_list.append(('ssn', match.group(), match.span()))
    
    return pii_list


def ner_pii(text: str) -> List[Tuple[str, str, Tuple[int, int]]]:
    """Extract PII using spaCy NER: PERSON, GPE (location), ORG (organization), DATE, TIME."""
    nlp = get_nlp_model()
    if nlp is None:
        return []
    
    doc = nlp(text)
    pii_list = []
    
    for ent in doc.ents:
        if ent.label_ in ('PERSON', 'GPE', 'ORG', 'DATE', 'TIME', 'FAC', 'PRODUCT'):
            # Map entity labels to PII types
            if ent.label_ == 'PERSON':
                entity_type = 'person'
            elif ent.label_ == 'GPE':
                entity_type = 'location'
            elif ent.label_ == 'ORG':
                entity_type = 'organization'
            elif ent.label_ in ('DATE', 'TIME'):
                entity_type = 'date_time'
            else:
                entity_type = 'medical_facility'  # For facilities/products
            
            pii_list.append((entity_type, ent.text, (ent.start_char, ent.end_char)))
    
    return pii_list


def normalize_phone(raw_phone: str) -> str:
    """Normalize phone number to digits only."""
    digits = re.sub(r'\D', '', raw_phone)
    return digits


def normalize_email(raw_email: str) -> str:
    """Normalize email to lowercase."""
    return raw_email.lower()


def normalize_date(raw_date: str) -> str:
    """Normalize date; return as-is for now."""
    return raw_date


def extract_pii_from_ocr(
    ocr_results: List[Dict],
    ocr_text: str
) -> List[Dict]:
    """
    Extract PII from OCR results and combined text.
    Returns list of {type, raw_text, normalized, bbox, confidence, source}.
    """
    pii_items = []
    
    # Get regex-based PII
    regex_pii = detect_regex_pii(ocr_text)
    # Get NER-based PII
    ner_pii_list = ner_pii(ocr_text)
    
    # Merge PII lists
    all_pii = regex_pii + ner_pii_list
    
    # Deduplicate and find corresponding OCR result for each PII
    seen = set()
    for pii_type, matched_text, (start_pos, end_pos) in all_pii:
        key = (pii_type, matched_text)
        if key in seen:
            continue
        seen.add(key)
        
        # Find corresponding OCR result
        best_bbox = None
        best_conf = 0.0
        best_source = 'regex' if pii_type in ('email', 'phone', 'date', 'aadhar', 'credit_card', 'ssn', 'hospital_id', 'bed_number', 'age_sex', 'patient_name', 'doctor_name', 'medical_info') else 'spacy'
        
        for ocr_item in ocr_results:
            if matched_text.lower() in ocr_item['text'].lower() or ocr_item['text'].lower() in matched_text.lower():
                if ocr_item['confidence'] > best_conf:
                    best_bbox = ocr_item['bbox']
                    best_conf = ocr_item['confidence']
                    best_source = ocr_item.get('source', 'unknown')
        
        # Normalize based on type
        if pii_type == 'phone':
            normalized = normalize_phone(matched_text)
        elif pii_type == 'email':
            normalized = normalize_email(matched_text)
        elif pii_type == 'date':
            normalized = normalize_date(matched_text)
        else:
            normalized = matched_text
        
        pii_item = {
            'type': pii_type,
            'raw_text': matched_text,
            'normalized': normalized,
            'bbox': best_bbox or [0, 0, 0, 0],
            'confidence': best_conf if best_bbox else 0.5,
            'source': best_source
        }
        pii_items.append(pii_item)
    
    # IMPORTANT: Also capture individual OCR results that might be handwritten medical notes
    # These often don't match full patterns but are still PII (treatment details, doctor notes, etc.)
    medical_keywords = ['treatment', 'advised', 'medication', 'tab', 'cap', 'syrup', 'injection', 
                       'mg', 'ml', 'dose', 'therapy', 'days', 'times', 'daily', 'bd', 'tid', 'qid',
                       'diagnosis', 'condition', 'prescription', 'follow', 'review', 'investigation']
    
    for ocr_item in ocr_results:
        text_lower = ocr_item['text'].lower()
        # Check if this OCR item contains medical keywords or is already captured
        already_captured = any(pii['raw_text'].lower() in text_lower or text_lower in pii['raw_text'].lower() 
                              for pii in pii_items)
        
        if not already_captured:
            # Check if it contains medical keywords or looks like handwritten notes (short phrases with medical context)
            is_medical = any(keyword in text_lower for keyword in medical_keywords)
            # Also capture short text snippets that might be treatment names/notes (3-50 chars)
            is_short_note = 3 <= len(ocr_item['text'].strip()) <= 50 and ocr_item['confidence'] < 0.7
            
            if is_medical or is_short_note:
                pii_item = {
                    'type': 'medical_note',
                    'raw_text': ocr_item['text'],
                    'normalized': ocr_item['text'].strip(),
                    'bbox': ocr_item['bbox'],
                    'confidence': ocr_item['confidence'],
                    'source': ocr_item.get('source', 'ocr')
                }
                pii_items.append(pii_item)
    
    return pii_items
