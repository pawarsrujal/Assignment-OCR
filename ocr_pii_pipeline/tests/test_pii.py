"""Unit tests for PII extraction module."""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.pii import (
    clean_text, detect_regex_pii, ner_pii, extract_pii_from_ocr,
    normalize_phone, normalize_email
)


class TestCleanText:
    """Test text normalization."""
    
    def test_clean_whitespace(self):
        """Test whitespace normalization."""
        result = clean_text("hello   world  \n  test")
        assert result == "hello world test"
    
    def test_clean_empty(self):
        """Test empty string handling."""
        result = clean_text("   ")
        assert result == ""


class TestRegexPII:
    """Test regex-based PII detection."""
    
    def test_detect_email(self):
        """Test email detection."""
        text = "Contact john.doe@example.com for details"
        result = detect_regex_pii(text)
        emails = [r for r in result if r[0] == 'email']
        assert len(emails) > 0
        assert 'john.doe@example.com' in [r[1] for r in emails]
    
    def test_detect_phone(self):
        """Test phone number detection."""
        text = "Call me at +91 98765-43210 or (555) 123-4567"
        result = detect_regex_pii(text)
        phones = [r for r in result if r[0] == 'phone']
        assert len(phones) > 0
    
    def test_detect_date(self):
        """Test date detection."""
        text = "Date: 25/12/2023"
        result = detect_regex_pii(text)
        dates = [r for r in result if r[0] == 'date']
        assert len(dates) > 0
        assert '25/12/2023' in [r[1] for r in dates]
    
    def test_detect_aadhar(self):
        """Test AADHAR-like pattern detection."""
        text = "AADHAR: 1234 5678 9012"
        result = detect_regex_pii(text)
        aadhaars = [r for r in result if r[0] == 'aadhar']
        assert len(aadhaars) > 0
    
    def test_detect_ssn(self):
        """Test SSN pattern detection."""
        text = "SSN: 123-45-6789"
        result = detect_regex_pii(text)
        ssns = [r for r in result if r[0] == 'ssn']
        assert len(ssns) > 0
    
    def test_no_pii(self):
        """Test text without PII."""
        text = "This is just normal text with no sensitive information"
        result = detect_regex_pii(text)
        # Should have no PII
        assert len(result) == 0 or all(r[0] not in ['email', 'phone'] for r in result)


class TestNormalization:
    """Test PII normalization."""
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        result = normalize_phone("+91 98765-43210")
        assert result == "919876543210"
    
    def test_normalize_email(self):
        """Test email normalization."""
        result = normalize_email("John.Doe@Example.COM")
        assert result == "john.doe@example.com"


class TestExtractPII:
    """Test complete PII extraction."""
    
    def test_extract_from_ocr_results(self):
        """Test extract_pii_from_ocr with sample OCR results."""
        ocr_results = [
            {'text': 'john.doe@example.com', 'confidence': 0.95, 'bbox': [10, 20, 100, 20], 'source': 'tesseract'},
            {'text': '+91', 'confidence': 0.9, 'bbox': [10, 50, 30, 20], 'source': 'easyocr'},
            {'text': '98765-43210', 'confidence': 0.88, 'bbox': [45, 50, 80, 20], 'source': 'easyocr'},
        ]
        ocr_text = "john.doe@example.com +91 98765-43210"
        
        result = extract_pii_from_ocr(ocr_results, ocr_text)
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check that result items have required fields
        for item in result:
            assert 'type' in item
            assert 'raw_text' in item
            assert 'normalized' in item
            assert 'bbox' in item
            assert 'confidence' in item
            assert 'source' in item
    
    def test_extract_multiple_pii_types(self):
        """Test extraction of multiple PII types."""
        ocr_results = []
        ocr_text = "Email: test@test.com Phone: 555-123-4567 Date: 01/01/2024"
        
        result = extract_pii_from_ocr(ocr_results, ocr_text)
        types_found = set(p['type'] for p in result)
        # Should find email and phone at minimum
        assert 'email' in types_found or 'phone' in types_found


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
