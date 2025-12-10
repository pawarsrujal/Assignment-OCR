# 🔍 OCR PII Pipeline - Streamlit Web App

A user-friendly web interface for the OCR → PII Extraction & Redaction Pipeline.

## 🚀 Quick Start

### Option 1: Using Batch File (Easiest)
```bash
# Double-click or run:
run_app.bat
```

### Option 2: Using Command Line
```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

---

## 📋 Features

✅ **Drag & Drop Upload** - Easy image upload interface  
✅ **Real-time Processing** - See results instantly  
✅ **Interactive JSON Viewer** - Expandable, formatted JSON response  
✅ **Side-by-Side Comparison** - Original vs Redacted images  
✅ **Adjustable Settings** - Configure confidence threshold, upscaling, redaction  
✅ **Detailed PII Breakdown** - Expandable cards for each detected item  
✅ **Download Options** - Save JSON and redacted images  
✅ **Full OCR Text Display** - View complete extracted text  

---

## 🎯 How to Use

### 1. Upload Image
- Click "Browse files" or drag & drop an image
- Supported formats: JPEG, PNG, BMP, TIFF

### 2. Configure Settings (Sidebar)
- **Minimum Confidence**: Adjust detection threshold (0.0-1.0)
  - Lower (0.3-0.4): More detections, may include false positives
  - Higher (0.6-0.8): Fewer detections, more precision
- **Upscale Image**: Enable for small/low-res text (2x scaling)
- **Enable Redaction**: Toggle black box masking of PII

### 3. Process
- Click "🚀 Process Image" button
- Wait for OCR and PII detection (first run may take 1-2 minutes)

### 4. View Results
- **Original Image**: Left side
- **Redacted Image**: Right side (if enabled)
- **JSON Response**: Full detection data
- **PII Details**: Expandable cards with confidence, bbox, etc.
- **OCR Text**: Complete extracted text

### 5. Download
- **📥 Download JSON**: Save detection results
- **📥 Download Redacted Image**: Save masked version

---

## 🎨 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────────┐
│  🔍 OCR → PII Extraction & Redaction Pipeline          │
│  Upload an image to extract text and detect PII        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ 📷 Original      │  │ 🔒 Redacted      │           │
│  │    Image         │  │    Image         │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  🚀 Process Image                                      │
│                                                         │
│  📄 JSON Response                                      │
│  {                                                      │
│    "filename": "page_30.jpg",                          │
│    "pii_count": 9,                                     │
│    ...                                                 │
│  }                                                     │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration Options

### Sidebar Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Minimum Confidence | 0.4 | Threshold for PII detection (0.0-1.0) |
| Upscale Image | False | 2x image scaling for small text |
| Enable Redaction | True | Mask PII with black boxes |

### PII Types Detected

- 📧 **Email** - Email addresses
- 📞 **Phone** - Phone numbers (various formats)
- 📅 **Date** - Date patterns
- 👤 **Person** - Names (via NER)
- 🏢 **Organization** - Company/org names
- 📍 **Location** - Place names
- 🆔 **AADHAR** - 12-digit ID
- 🆔 **SSN** - Social Security Numbers
- 💳 **Credit Card** - Card numbers

---

## 🔧 Technical Details

### Architecture
```
User Upload → Preprocessing → OCR (Tesseract/EasyOCR) → PII Detection (Regex/NER) → Redaction → Display
```

### Processing Pipeline
1. **Image Upload**: Temporary file storage
2. **Preprocessing**: Deskew, CLAHE, denoise, binarize
3. **OCR Ensemble**: Tesseract + EasyOCR with deduplication
4. **PII Extraction**: Regex patterns + spaCy NER
5. **Redaction**: Black box masking (optional)
6. **JSON Output**: Structured response with bbox, confidence, source

### Performance
- **First Run**: 1-2 minutes (EasyOCR model loading)
- **Subsequent Runs**: 5-10 seconds per image
- **Memory**: ~2GB RAM (EasyOCR neural network)

---

## 📊 Output Format

### JSON Structure
```json
{
  "filename": "sample.jpg",
  "processed_at": "2025-12-09T12:34:56Z",
  "ocr_text": "Full extracted text...",
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

### Fields Explained
- `filename`: Original uploaded filename
- `processed_at`: UTC timestamp
- `ocr_text`: Complete OCR-extracted text
- `pii_count`: Total PII items found
- `pii`: Array of detected PII items
  - `type`: Category (email, phone, person, etc.)
  - `raw_text`: Text as extracted
  - `normalized`: Cleaned/standardized version
  - `bbox`: [x, y, width, height] in pixels
  - `confidence`: Detection confidence (0.0-1.0)
  - `source`: Detection method (regex/spacy/tesseract/easyocr)

---

## 🛠️ Troubleshooting

### App won't start
```bash
# Check if Streamlit is installed
pip install streamlit

# Run directly
streamlit run app.py
```

### "Module not found" errors
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Slow processing
- **First run**: EasyOCR downloads models (~100MB), takes 1-2 min
- **Subsequent runs**: Should be faster
- **Large images**: Disable upscaling or resize before upload
- **No GPU**: EasyOCR runs on CPU (slower but works)

### No PII detected
- Lower confidence threshold (try 0.3)
- Check OCR text output - if empty, OCR failed
- Try enabling upscale for small text
- Verify image quality and resolution

### Tesseract warning
- **Optional**: Tesseract not installed (app works with EasyOCR only)
- **Install**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Benefit**: Faster OCR processing when available

---

## 💡 Tips for Best Results

### Image Quality
- **Resolution**: Minimum 300 DPI recommended
- **Format**: JPEG/PNG with good contrast
- **Size**: Up to 10MB (larger images take longer)

### Settings Optimization
| Use Case | Confidence | Upscale | Notes |
|----------|-----------|---------|-------|
| Printed docs | 0.6-0.8 | No | High accuracy, clear text |
| Handwritten | 0.3-0.4 | Yes | Lower threshold for harder OCR |
| Small text | 0.4-0.5 | Yes | Enable upscaling |
| Mixed quality | 0.4-0.5 | No | Balanced approach |

---

## 🔒 Privacy & Security

⚠️ **Important Notes:**
- All processing is **local** - no data sent to cloud
- Uploaded images are **temporary** - deleted after processing
- Use **redaction** before sharing images with detected PII
- **Download** both JSON and redacted images for archival

---

## 📁 Project Structure

```
ocr_pii_pipeline/
├── app.py              # Streamlit web application
├── run_app.bat         # Windows batch launcher
├── run_pipeline.py     # CLI version
├── pipeline/           # Core OCR/PII modules
├── examples/           # Sample images
└── requirements.txt    # Python dependencies
```

---

## 🆘 Support

### Common Issues
1. **Port already in use**: Change port with `streamlit run app.py --server.port 8502`
2. **Memory errors**: Close other applications, restart app
3. **Slow performance**: First run downloads models, be patient

### Getting Help
- Check main README.md for detailed documentation
- Review GETTING_STARTED.md for installation steps
- Run `python quick_test.py` to verify setup

---

## 🎓 Example Workflow

```bash
# 1. Start the app
run_app.bat

# 2. In browser:
#    - Upload page_30.jpg from examples folder
#    - Set confidence to 0.4
#    - Enable redaction
#    - Click "Process Image"

# 3. View results:
#    - See 9 PII items detected
#    - Compare original vs redacted images
#    - Expand JSON to see details

# 4. Download:
#    - Save JSON for records
#    - Save redacted image for sharing
```

---

## 🚀 Advanced Usage

### Custom Port
```bash
streamlit run app.py --server.port 8080
```

### Remote Access
```bash
streamlit run app.py --server.address 0.0.0.0
```

### Disable Browser Auto-open
```bash
streamlit run app.py --server.headless true
```

---

**Ready to go!** 🎉

Run: `run_app.bat` or `streamlit run app.py`

Then visit: http://localhost:8501
