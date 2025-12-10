# OCR → PII Extraction & Redaction Pipeline

A complete, self-contained Python pipeline for:
- **OCR**: Extract text from scanned/handwritten JPEG images using ensemble of Tesseract + EasyOCR
- **PII Detection**: Identify personally identifiable information (emails, phones, dates, AADHAR, SSN, etc.) using regex + spaCy NER
- **Redaction**: Optionally mask detected PII regions in images (black box or blur)
- **Output**: JSON files with detected PII and optional redacted images

## Features

✓ Robust handwriting OCR with preprocessing (deskew, CLAHE, bilateral filtering, binarization)  
✓ Ensemble OCR with intelligent deduplication and fuzzy text matching  
✓ Multi-pattern PII detection (email, phone, date, AADHAR, SSN, credit card)  
✓ Named Entity Recognition (NER) for person/location/organization extraction  
✓ Image redaction with black box or Gaussian blur  
✓ Batch processing via CLI with progress tracking  
✓ Comprehensive unit tests (pytest)  
✓ Configurable confidence thresholds and preprocessing parameters  
✓ Local processing—no cloud APIs required  

---

## Installation

### 1. System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev
```

#### macOS
```bash
brew install tesseract
```

#### Windows
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install (default path: `C:\Program Files\Tesseract-OCR`)
3. Set environment variable (or the code will auto-detect):
   ```powershell
   setx PYTESSERACT_PATH "C:\Program Files\Tesseract-OCR\pytesseract.py"
   ```

### 2. Python Environment

```bash
# Clone or navigate to project directory
cd ocr_pii_pipeline

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model (required for NER)
python -m spacy download en_core_web_sm
```

---

## Project Structure

```
ocr_pii_pipeline/
├─ README.md                 # This file
├─ requirements.txt          # Python package dependencies
├─ run_pipeline.py           # Main CLI entrypoint
├─ pipeline/
│  ├─ __init__.py
│  ├─ preprocess.py          # Image preprocessing (deskew, enhance, binarize)
│  ├─ ocr.py                 # Tesseract + EasyOCR ensemble
│  ├─ pii.py                 # Regex + spaCy NER for PII extraction
│  ├─ redact.py              # Image redaction (black/blur)
│  └─ utils.py               # Helper functions (JSON, image I/O, bbox utilities)
├─ tests/
│  ├─ test_preprocess.py     # Unit tests for preprocessing
│  ├─ test_ocr.py            # Unit tests for OCR
│  └─ test_pii.py            # Unit tests for PII detection
└─ examples/
   ├─ sample1.jpg            # (Optional) sample image for testing
   └─ expected_output_sample1.json  # (Optional) expected JSON output format
```

---

## Quick Start

### Basic Usage

```bash
# Process all JPEG images in a folder
python run_pipeline.py --input ./images --output ./results

# With redaction enabled
python run_pipeline.py --input ./images --output ./results --redact

# With custom confidence threshold
python run_pipeline.py --input ./images --output ./results --min_confidence 0.5

# Upscale small text for better OCR
python run_pipeline.py --input ./images --output ./results --upscale
```

### Sample Command

```bash
python run_pipeline.py --input examples/ --output out/ --redact --min_confidence 0.4
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pii.py -v

# Run with coverage
pytest tests/ --cov=pipeline --cov-report=html
```

---

## Output Format

### JSON Output (`<image_name>.pii.json`)

```json
{
  "filename": "sample1.jpg",
  "processed_at": "2025-12-09T12:34:56Z",
  "ocr_text": "Contact john.doe@example.com or call +91 98765-43210",
  "pii_count": 2,
  "pii": [
    {
      "type": "email",
      "raw_text": "john.doe@example.com",
      "normalized": "john.doe@example.com",
      "bbox": [120, 45, 240, 18],
      "confidence": 0.92,
      "source": "easyocr"
    },
    {
      "type": "phone",
      "raw_text": "+91 98765-43210",
      "normalized": "919876543210",
      "bbox": [80, 200, 150, 18],
      "confidence": 0.86,
      "source": "tesseract"
    }
  ]
}
```

**Fields:**
- `filename`: Input image filename
- `processed_at`: UTC timestamp of processing
- `ocr_text`: Complete OCR-extracted text
- `pii_count`: Total PII items detected
- `pii`: Array of detected PII items with:
  - `type`: Category (email, phone, date, person, organization, location, aadhar, ssn, credit_card)
  - `raw_text`: Text as extracted from image
  - `normalized`: Cleaned/standardized version
  - `bbox`: [x, y, width, height] bounding box in image
  - `confidence`: Detection confidence (0.0–1.0)
  - `source`: Detection source (regex, spacy, tesseract, easyocr, ensemble)

### Redacted Image Output

If `--redact` flag is used, a redacted image is saved as `<image_name>.redacted.jpg` with:
- Black boxes (default) or Gaussian blur masking PII regions
- Original image preserved if no PII detected

---

## Configuration & Tuning

### CLI Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input` | Required | Input folder path containing JPEG/PNG images |
| `--output` | Required | Output folder for JSON and redacted images |
| `--min_confidence` | 0.4 | Confidence threshold for OCR results (0.0–1.0) |
| `--redact` | False | Enable image redaction and save redacted versions |
| `--upscale` | False | Upscale images to improve OCR on small text |

### Preprocessing Parameters (in `pipeline/preprocess.py`)

#### CLAHE (Contrast Limited Adaptive Histogram Equalization)
```python
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
```
- **clipLimit**: Higher → more contrast (default: 3.0, range: 1–5)
- **tileGridSize**: Larger → more global effect (default: 8×8)

#### Bilateral Filtering (denoise)
```python
denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
```
- **diameter**: Higher → more smoothing (default: 9, range: 5–15)
- **sigma values**: Control color/spatial smoothing (default: 75, range: 50–100)

#### Morphological Operations (noise removal)
```python
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
```
- **kernel size**: Larger → removes larger noise (default: 3×3, try: 5×5)

#### Upscaling
```python
upscale_image(image, scale=2.0)  # 2x larger
```
- **scale**: Multiplication factor (default: 2.0, range: 1.5–4.0)

### PII Detection Thresholds (in `pipeline/pii.py`)

**Confidence filtering** in `extract_pii_from_ocr()`:
```python
pii_items = [p for p in pii_items if p['confidence'] >= min_confidence]
```
- Lower `--min_confidence` → more PII detected (higher false positives)
- Higher `--min_confidence` → fewer PII items (fewer false positives)

**Fuzzy matching threshold** in `ensemble_ocr()`:
```python
fuzz.ratio(text1.lower(), text2.lower()) / 100.0 >= 0.75
```
- Controls text similarity for deduplication (0.0–1.0, default: 0.75)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pytesseract'"
→ Run `pip install -r requirements.txt`

### "Tesseract is not installed or not in PATH"
→ Install Tesseract (see Installation section) and ensure it's in system PATH
→ Or manually set in code: `pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### "Can't load model 'en_core_web_sm'"
→ Run `python -m spacy download en_core_web_sm`

### Low OCR accuracy on handwritten text
1. **Enable upscaling**: `--upscale` flag
2. **Lower confidence threshold**: Try `--min_confidence 0.3`
3. **Tweak preprocessing**:
   - Increase CLAHE `clipLimit` for more contrast
   - Reduce bilateral filter `diameter` for sharper text
   - Adjust morphological kernel size

### No PII detected in JSON
1. **Check OCR text**: Verify `ocr_text` field in JSON is not empty
2. **Verify patterns**: Use regex tester to confirm expected formats
3. **Lower confidence**: Try `--min_confidence 0.2`
4. **Check NER**: Ensure spaCy model is properly loaded (`python -m spacy download en_core_web_sm`)

### Redacted images have incorrect masks
1. **Verify bbox values**: Check JSON output for non-zero bbox coordinates
2. **Image corruption**: Ensure input images are valid JPEG/PNG
3. **Method selection**: Try both `--redact` modes (currently black box is default; modify `redact.py` for blur)

---

## Performance Tips

1. **Batch processing**: Use CLI to process entire folders in parallel
2. **Memory usage**: EasyOCR loads a neural network; use GPU if available (modify `ocr.py: gpu=True`)
3. **Speed**: Tesseract is faster but less accurate; EasyOCR is slower but handles handwriting better
4. **Smaller images**: Preprocess with `cv2.resize()` for faster processing (add to `preprocess.py`)

---

## Privacy & Security

⚠️ **Important**: This pipeline processes sensitive PII locally without external APIs.

**Best practices:**
- Always redact before archiving or sharing images: `--redact` flag
- Store output JSON securely; contains sensitive information
- Consider encrypting output directory
- Run locally on trusted machines (no cloud upload)
- Audit regex patterns for your specific use cases

---

## Advanced Usage

### Using the Pipeline Programmatically

```python
from pipeline.preprocess import load_image, preprocess_full_pipeline
from pipeline.ocr import ensemble_ocr
from pipeline.pii import extract_pii_from_ocr
from pipeline.redact import redact_image, save_image
from pipeline.utils import save_json

# Load and preprocess image
bgr = load_image('sample.jpg')
preprocessed = preprocess_full_pipeline(bgr, upscale=True)

# Run OCR
ocr_results = ensemble_ocr(preprocessed, conf_threshold=0.4)
ocr_text = " ".join([r['text'] for r in ocr_results])

# Extract PII
pii_items = extract_pii_from_ocr(ocr_results, ocr_text)

# Redact and save
redacted = redact_image(bgr, pii_items, method='black')
save_image(redacted, 'output_redacted.jpg')
save_json({'pii': pii_items}, 'output.json')
```

### Customizing OCR Ensemble Weights

```python
from pipeline.ocr import ensemble_ocr

# Prioritize EasyOCR for handwriting
weights = {'easyocr': 0.8, 'tesseract': 0.2}
results = ensemble_ocr(image, weights=weights)
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_pii.py::TestRegexPII -v

# Generate coverage report
pytest tests/ --cov=pipeline --cov-report=term-missing
```

**Test coverage:**
- `test_preprocess.py`: Image loading, deskewing, enhancement, binarization
- `test_ocr.py`: Tesseract and EasyOCR output validation
- `test_pii.py`: Regex PII detection, spaCy NER, normalization, extraction

---

## Requirements

See `requirements.txt` for complete list:
- **opencv-python**: Image processing
- **pillow**: Image I/O (PIL)
- **numpy**: Numerical operations
- **pytesseract**: Tesseract OCR wrapper
- **easyocr**: Neural network-based OCR
- **spacy**: NLP and Named Entity Recognition
- **rapidfuzz**: Fuzzy string matching
- **matplotlib**: Visualization (optional)
- **pytest**: Unit testing

---

## License

This project is provided as-is for educational and production use.

---

## Contributing

Suggestions for improvements:
- [ ] GPU support for EasyOCR
- [ ] Support for more document languages
- [ ] Confidence score calibration
- [ ] Custom PII pattern templates
- [ ] Batch processing with multiprocessing
- [ ] Web API wrapper (FastAPI)
- [ ] Docker containerization

---

## Support & Documentation

For issues:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Test with provided sample images in `examples/`
4. Review unit tests for usage examples

---

## Example JSON Output (Full)

```json
{
  "filename": "invoice_2023.jpg",
  "processed_at": "2025-12-09T14:22:33Z",
  "ocr_text": "Invoice #12345 Customer: John Doe Email: john.doe@company.com Phone: +1-555-987-6543 Date: 15/12/2023",
  "pii_count": 4,
  "pii": [
    {
      "type": "person",
      "raw_text": "John Doe",
      "normalized": "John Doe",
      "bbox": [100, 50, 150, 30],
      "confidence": 0.95,
      "source": "spacy"
    },
    {
      "type": "email",
      "raw_text": "john.doe@company.com",
      "normalized": "john.doe@company.com",
      "bbox": [150, 100, 250, 25],
      "confidence": 0.99,
      "source": "regex"
    },
    {
      "type": "phone",
      "raw_text": "+1-555-987-6543",
      "normalized": "15559876543",
      "bbox": [120, 150, 200, 25],
      "confidence": 0.88,
      "source": "regex"
    },
    {
      "type": "date",
      "raw_text": "15/12/2023",
      "normalized": "15/12/2023",
      "bbox": [200, 200, 150, 25],
      "confidence": 0.92,
      "source": "regex"
    }
  ]
}
```

---

**Happy OCR-ing!** 🚀
