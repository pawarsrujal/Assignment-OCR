"""Streamlit web app for OCR → PII Extraction & Redaction Pipeline."""

import streamlit as st
import sys
from pathlib import Path
import json
import tempfile
import os
from PIL import Image
import numpy as np
import cv2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.preprocess import load_image, preprocess_full_pipeline
from pipeline.ocr import ensemble_ocr
from pipeline.pii import extract_pii_from_ocr
from pipeline.redact import redact_image
from pipeline.utils import get_timestamp, summarize_pii_counts, NumpyEncoder


# Page configuration
st.set_page_config(
    page_title="OCR PII Pipeline",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def process_uploaded_image(uploaded_file, min_confidence, upscale, redact_enabled):
    """Process uploaded image and return results."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Load and preprocess
        bgr = load_image(tmp_path)
        preprocessed = preprocess_full_pipeline(bgr, upscale=upscale)
        
        # OCR: ensemble method
        with st.spinner('Running OCR (this may take a minute on first run)...'):
            ocr_results = ensemble_ocr(preprocessed, conf_threshold=min_confidence)
        
        # Combine OCR text
        ocr_text = " ".join([r['text'] for r in ocr_results])
        
        # Extract PII
        with st.spinner('Extracting PII...'):
            pii_items = extract_pii_from_ocr(ocr_results, ocr_text)
        
        # Filter by confidence
        pii_items = [p for p in pii_items if p['confidence'] >= min_confidence]
        
        # Create JSON response
        json_response = {
            'filename': uploaded_file.name,
            'processed_at': get_timestamp(),
            'ocr_text': ocr_text,
            'pii_count': len(pii_items),
            'pii': pii_items
        }
        
        # Redact if enabled
        redacted_img = None
        if redact_enabled and len(pii_items) > 0:
            redacted_img = redact_image(bgr, pii_items, method='black')
        
        # Cleanup
        os.unlink(tmp_path)
        
        return json_response, bgr, redacted_img, pii_items
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None, None, None


def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🔍 OCR → PII Extraction & Redaction Pipeline")
    st.markdown("Upload an image to extract text and detect personally identifiable information (PII)")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    min_confidence = st.sidebar.slider(
        "Minimum Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Lower values (0.2-0.3) better for handwritten text. Higher values (0.6+) for printed text only."
    )
    
    upscale = st.sidebar.checkbox(
        "Upscale Image (2x)",
        value=False,
        help="Enable for small text or low-resolution images"
    )
    
    redact_enabled = st.sidebar.checkbox(
        "Enable Redaction",
        value=True,
        help="Mask detected PII regions with black boxes"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 PII Types Detected")
    st.sidebar.markdown("""
    - 📧 Email addresses
    - 📞 Phone numbers
    - 📅 Dates
    - 👤 Person names
    - 🏢 Organizations
    - 📍 Locations
    - 🆔 AADHAR, SSN, Credit Cards
    """)
    
    # Main content
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Upload a scanned document or image with text"
    )
    
    if uploaded_file is not None:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
        
        # Process button
        if st.button("🚀 Process Image", type="primary", use_container_width=True):
            with st.spinner('Processing image...'):
                json_response, original_bgr, redacted_img, pii_items = process_uploaded_image(
                    uploaded_file,
                    min_confidence,
                    upscale,
                    redact_enabled
                )
            
            if json_response:
                # Success message
                pii_counts = summarize_pii_counts(pii_items)
                counts_str = ", ".join([f"{count} {ptype}" for ptype, count in pii_counts.items()])
                st.success(f"✅ Processing complete! Found {len(pii_items)} PII items: {counts_str if counts_str else 'None'}")
                
                # Display results
                with col2:
                    if redacted_img is not None:
                        st.subheader("🔒 Redacted Image")
                        # Convert BGR to RGB for display
                        redacted_rgb = cv2.cvtColor(redacted_img, cv2.COLOR_BGR2RGB)
                        st.image(redacted_rgb, use_container_width=True)
                    else:
                        st.info("No PII detected or redaction disabled")
                
                # JSON Response
                st.subheader("📄 JSON Response")
                st.json(json.loads(json.dumps(json_response, cls=NumpyEncoder)))
                
                # Download buttons
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                
                with col_dl1:
                    # Download JSON
                    json_str = json.dumps(json_response, indent=2, cls=NumpyEncoder)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"{uploaded_file.name.split('.')[0]}.pii.json",
                        mime="application/json"
                    )
                
                with col_dl2:
                    # Download redacted image
                    if redacted_img is not None:
                        # Convert to PIL and save
                        redacted_pil = Image.fromarray(cv2.cvtColor(redacted_img, cv2.COLOR_BGR2RGB))
                        buf = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        redacted_pil.save(buf.name, format='JPEG')
                        
                        with open(buf.name, 'rb') as f:
                            st.download_button(
                                label="📥 Download Redacted Image",
                                data=f,
                                file_name=f"{uploaded_file.name.split('.')[0]}.redacted.jpg",
                                mime="image/jpeg"
                            )
                        os.unlink(buf.name)
                
                # Detailed PII breakdown
                if pii_items:
                    st.subheader("🔍 Detected PII Details")
                    
                    for idx, pii in enumerate(pii_items, 1):
                        with st.expander(f"{idx}. {pii['type'].upper()} - {pii['raw_text'][:50]}"):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write("**Type:**", pii['type'])
                                st.write("**Raw Text:**", pii['raw_text'])
                                st.write("**Normalized:**", pii['normalized'])
                            
                            with col_b:
                                st.write("**Confidence:**", f"{pii['confidence']:.2%}")
                                st.write("**Source:**", pii['source'])
                                st.write("**Bounding Box:**", pii['bbox'])
                
                # OCR Text
                with st.expander("📝 Full OCR Extracted Text"):
                    st.text_area(
                        "Extracted Text",
                        value=json_response['ocr_text'],
                        height=200,
                        disabled=True
                    )
    
    else:
        # Instructions when no file uploaded
        st.info("👆 Upload an image to get started")
        
        # Example usage
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            ### Steps:
            1. **Upload an image** - Click "Browse files" and select a document image
            2. **Configure settings** - Adjust confidence threshold and options in the sidebar
            3. **Process** - Click "Process Image" button
            4. **View results** - See detected PII, redacted image, and JSON output
            5. **Download** - Save JSON data and redacted image
            
            ### Tips:
            - Use **lower confidence** (0.3-0.4) for handwritten text
            - Use **higher confidence** (0.6-0.8) for printed text
            - Enable **upscale** for small or low-resolution text
            - **Redaction** masks PII regions with black boxes
            
            ### Supported Formats:
            - JPEG, PNG, BMP, TIFF
            - Scanned documents, photos, screenshots
            """)


if __name__ == '__main__':
    main()
