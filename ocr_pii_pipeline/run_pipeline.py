"""Main CLI entrypoint: process image folder through OCR → PII extraction → redaction pipeline."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.preprocess import load_image, preprocess_full_pipeline
from pipeline.ocr import ensemble_ocr
from pipeline.pii import extract_pii_from_ocr
from pipeline.redact import redact_image
from pipeline.utils import save_json, save_image, ensure_dir, get_timestamp, summarize_pii_counts


def process_image(
    image_path: str,
    output_dir: str,
    redact: bool = False,
    min_confidence: float = 0.4,
    upscale: bool = False
) -> Tuple[bool, str]:
    """
    Process single image: preprocess → OCR → PII extraction → redaction.
    Returns (success, summary_message).
    """
    try:
        filename = os.path.basename(image_path)
        print(f"Processing {filename}...", end=" ", flush=True)
        
        # Load and preprocess
        bgr = load_image(image_path)
        preprocessed = preprocess_full_pipeline(bgr, upscale=upscale)
        
        # OCR: ensemble method
        ocr_results = ensemble_ocr(preprocessed, conf_threshold=min_confidence)
        
        # Combine OCR text for PII extraction
        ocr_text = " ".join([r['text'] for r in ocr_results])
        
        # Extract PII
        pii_items = extract_pii_from_ocr(ocr_results, ocr_text)
        
        # Filter by confidence
        pii_items = [p for p in pii_items if p['confidence'] >= min_confidence]
        
        # Prepare output JSON
        pii_summary = {
            'filename': filename,
            'processed_at': get_timestamp(),
            'ocr_text': ocr_text,
            'pii_count': len(pii_items),
            'pii': pii_items
        }
        
        # Save PII JSON
        ensure_dir(output_dir)
        json_path = os.path.join(output_dir, f"{Path(filename).stem}.pii.json")
        save_json(pii_summary, json_path)
        
        # Optional: redact and save image
        if redact:
            redacted_img = redact_image(bgr, pii_items, method='black')
            redacted_path = os.path.join(output_dir, f"{Path(filename).stem}.redacted.jpg")
            save_image(redacted_img, redacted_path)
        
        # Generate summary message
        pii_counts = summarize_pii_counts(pii_items)
        counts_str = ", ".join([f"{count} {ptype}" for ptype, count in pii_counts.items()])
        summary = f"✓ {len(pii_items)} PII items found ({counts_str})"
        print(summary)
        
        return True, summary
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False, f"Error: {str(e)}"


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="OCR → PII Extraction & Redaction Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py --input examples/ --output out/ --min_confidence 0.5
  python run_pipeline.py --input . --output results/ --redact --min_confidence 0.6
        """
    )
    parser.add_argument('--input', type=str, required=True, help='Input folder containing JPEG images')
    parser.add_argument('--output', type=str, required=True, help='Output folder for JSON and redacted images')
    parser.add_argument('--min_confidence', type=float, default=0.4, help='Minimum OCR confidence threshold (0.0-1.0)')
    parser.add_argument('--redact', action='store_true', help='Enable image redaction (save redacted images)')
    parser.add_argument('--upscale', action='store_true', help='Upscale images to improve OCR on small text')
    
    args = parser.parse_args()
    
    # Validate input folder
    if not os.path.isdir(args.input):
        print(f"Error: Input folder '{args.input}' does not exist.")
        sys.exit(1)
    
    # Find image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [
        os.path.join(args.input, f)
        for f in os.listdir(args.input)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    if not image_files:
        print(f"No image files found in '{args.input}'")
        sys.exit(0)
    
    print(f"\n{'='*60}")
    print(f"OCR → PII Extraction & Redaction Pipeline")
    print(f"{'='*60}")
    print(f"Input folder: {args.input}")
    print(f"Output folder: {args.output}")
    print(f"Min confidence: {args.min_confidence}")
    print(f"Redaction enabled: {args.redact}")
    print(f"Images to process: {len(image_files)}")
    print(f"{'='*60}\n")
    
    # Process each image
    success_count = 0
    for image_path in sorted(image_files):
        success, _ = process_image(
            image_path,
            args.output,
            redact=args.redact,
            min_confidence=args.min_confidence,
            upscale=args.upscale
        )
        if success:
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Pipeline Complete")
    print(f"{'='*60}")
    print(f"Processed: {success_count}/{len(image_files)} images")
    print(f"Output directory: {args.output}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
