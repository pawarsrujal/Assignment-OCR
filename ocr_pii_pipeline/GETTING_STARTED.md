# Getting Started Guide

## Quick Start (3 Steps)

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd ocr_pii_pipeline

# Run automated setup
python setup.py
```

**What this does:**
- Installs all Python packages from `requirements.txt`
- Downloads spaCy English model
- Verifies Tesseract installation
- Runs basic tests

### 2. Verify Installation

```powershell
# Run quick tests
python quick_test.py
```

**Expected output:**
```
✓ PASS   Preprocessing
✓ PASS   PII Detection
✓ PASS   OCR
✓ PASS   Redaction

4/4 tests passed
```

### 3. Run the Pipeline

```powershell
# Process your images
python run_pipeline.py --input examples/ --output out/ --redact --min_confidence 0.4
```

**What you'll get:**
- JSON files with detected PII: `out/page_30.pii.json`, `out/page_35.pii.json`
- Redacted images: `out/page_30.redacted.jpg`, `out/page_35.redacted.jpg`

---

## Manual Installation (If Automated Setup Fails)

### Step 1: Install Tesseract OCR

#### Windows
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (recommended path: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or set in code:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

#### Verify Installation
```powershell
tesseract --version
```

### Step 2: Install Python Packages

```powershell
pip install opencv-python pillow numpy pytesseract easyocr spacy rapidfuzz matplotlib pytest
```

### Step 3: Download spaCy Model

```powershell
python -m spacy download en_core_web_sm
```

---

## Understanding the Output

### JSON Structure (`*.pii.json`)

```json
{
  "filename": "page_30.jpg",
  "processed_at": "2025-12-09T12:34:56Z",
  "ocr_text": "Full extracted text from image...",
  "pii_count": 3,
  "pii": [
    {
      "type": "email",
      "raw_text": "john.doe@example.com",
      "normalized": "john.doe@example.com",
      "bbox": [120, 45, 240, 18],
      "confidence": 0.92,
      "source": "regex"
    }
  ]
}
```

**PII Types Detected:**
- `email` - Email addresses
- `phone` - Phone numbers (various formats)
- `date` - Date patterns (DD/MM/YYYY, etc.)
- `person` - Person names (via spaCy NER)
- `organization` - Company/org names (via spaCy NER)
- `location` - Place names (via spaCy NER)
- `aadhar` - AADHAR card numbers (12 digits)
- `ssn` - Social Security Numbers
- `credit_card` - Credit card numbers

### Redacted Images (`*.redacted.jpg`)

Black boxes cover detected PII regions. Original image preserved if no PII found.

---

## Common Use Cases

### Case 1: Low Confidence (More PII Detected)
```powershell
python run_pipeline.py --input examples/ --output out/ --min_confidence 0.3
```
**Use when:** Handwritten text, poor image quality, want to catch more PII

### Case 2: High Confidence (Fewer False Positives)
```powershell
python run_pipeline.py --input examples/ --output out/ --min_confidence 0.7
```
**Use when:** Printed text, good image quality, want precision over recall

### Case 3: Small Text (Upscale for Better OCR)
```powershell
python run_pipeline.py --input examples/ --output out/ --upscale
```
**Use when:** Tiny fonts, low-resolution scans

### Case 4: JSON Only (No Redaction)
```powershell
python run_pipeline.py --input examples/ --output out/
```
**Use when:** Only need PII detection data, not redacted images

---

## Troubleshooting

### Issue: "Tesseract is not installed or not in PATH"

**Solution 1:** Install Tesseract (see Manual Installation above)

**Solution 2:** Manually set path in `pipeline/ocr.py`:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: "Can't load model 'en_core_web_sm'"

**Solution:**
```powershell
python -m spacy download en_core_web_sm
```

### Issue: Low OCR Accuracy

**Try these options:**
1. Enable upscaling: `--upscale`
2. Lower confidence: `--min_confidence 0.3`
3. Preprocess images externally (deskew, enhance contrast)
4. Check image resolution (min 300 DPI recommended)

### Issue: No PII Detected

**Check:**
1. Verify OCR text in JSON (`ocr_text` field)
2. Lower confidence threshold: `--min_confidence 0.2`
3. Check if text matches expected patterns (email format, phone format, etc.)
4. View raw OCR output to see what text was extracted

### Issue: Out of Memory

**Solutions:**
1. Process fewer images at a time
2. Reduce image size before processing
3. Disable upscaling
4. Use GPU for EasyOCR (modify `ocr.py: gpu=True`)

---

## Running Tests

```powershell
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_pii.py -v

# With coverage
pytest tests/ --cov=pipeline --cov-report=html
```

**View coverage report:**
Open `htmlcov/index.html` in browser

---

## Project Structure Explained

```
ocr_pii_pipeline/
├─ pipeline/           # Core modules
│  ├─ preprocess.py    # Image enhancement (deskew, CLAHE, denoise)
│  ├─ ocr.py          # Tesseract + EasyOCR ensemble
│  ├─ pii.py          # Regex patterns + spaCy NER
│  ├─ redact.py       # Black box / blur masking
│  └─ utils.py        # JSON/image I/O, helpers
│
├─ tests/             # Unit tests (pytest)
├─ examples/          # Sample images (page_30.jpg, page_35.jpg)
├─ run_pipeline.py    # Main CLI entrypoint
├─ setup.py           # Automated installation
├─ quick_test.py      # Quick functionality verification
└─ requirements.txt   # Python dependencies
```

---

## Next Steps

1. ✓ **Run setup**: `python setup.py`
2. ✓ **Verify**: `python quick_test.py`
3. ✓ **Process images**: `python run_pipeline.py --input examples/ --output out/ --redact`
4. Check output in `out/` folder
5. Review JSON files for detected PII
6. View redacted images

---

## Advanced: Programmatic Usage

```python
from pipeline.preprocess import load_image, preprocess_full_pipeline
from pipeline.ocr import ensemble_ocr
from pipeline.pii import extract_pii_from_ocr
from pipeline.redact import redact_image
from pipeline.utils import save_json, save_image

# Load and preprocess
bgr = load_image('examples/page_30.jpg')
preprocessed = preprocess_full_pipeline(bgr, upscale=True)

# OCR
ocr_results = ensemble_ocr(preprocessed, conf_threshold=0.4)
ocr_text = " ".join([r['text'] for r in ocr_results])

# Extract PII
pii_items = extract_pii_from_ocr(ocr_results, ocr_text)

# Redact and save
redacted = redact_image(bgr, pii_items, method='black')
save_image(redacted, 'output_redacted.jpg')
save_json({'pii': pii_items}, 'output.json')
```

---

## Support

For issues:
1. Check this guide
2. Run `python quick_test.py` to diagnose
3. Review README.md for detailed documentation
4. Check test files for usage examples

---

**Ready to go!** 🚀

Run: `python run_pipeline.py --input examples/ --output out/ --redact`
