"""Setup script to install dependencies and verify installation."""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Run setup steps."""
    print("\n" + "="*60)
    print("OCR PII Pipeline - Setup & Installation")
    print("="*60)
    
    # Step 1: Install Python packages
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Step 1: Installing Python packages"
    ):
        print("\n⚠ Failed to install some packages. Please check your internet connection.")
        return False
    
    # Step 2: Download spaCy model
    if not run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Step 2: Downloading spaCy English model"
    ):
        print("\n⚠ Failed to download spaCy model. Please try manually:")
        print("   python -m spacy download en_core_web_sm")
    
    # Step 3: Verify Tesseract installation
    print("\n" + "="*60)
    print("Step 3: Verifying Tesseract OCR installation")
    print("="*60)
    try:
        result = subprocess.run("tesseract --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            print("✓ Tesseract is installed")
        else:
            print("✗ Tesseract not found in PATH")
            print("\nPlease install Tesseract:")
            print("  - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  - Linux: sudo apt-get install tesseract-ocr")
            print("  - macOS: brew install tesseract")
            return False
    except Exception as e:
        print(f"✗ Error checking Tesseract: {e}")
        return False
    
    # Step 4: Run basic tests
    if not run_command(
        f"{sys.executable} -m pytest tests/test_pii.py::TestCleanText -v",
        "Step 4: Running basic tests"
    ):
        print("\n⚠ Some tests failed, but installation may still work.")
    
    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Place your images in the 'examples/' folder")
    print("  2. Run the pipeline:")
    print("     python run_pipeline.py --input examples/ --output out/ --redact")
    print("\n")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
