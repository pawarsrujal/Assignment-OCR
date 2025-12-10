"""Check if all dependencies are installed and configured correctly."""

import sys
import subprocess


def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name:20} installed")
        return True
    except ImportError:
        print(f"✗ {package_name:20} NOT installed")
        return False


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(
            "tesseract --version",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR        installed ({version})")
            return True
        else:
            print(f"✗ Tesseract OCR        NOT found in PATH")
            return False
    except Exception as e:
        print(f"✗ Tesseract OCR        NOT found ({e})")
        return False


def check_spacy_model():
    """Check if spaCy English model is downloaded."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print(f"✓ spaCy model          en_core_web_sm loaded")
        return True
    except Exception:
        print(f"✗ spaCy model          en_core_web_sm NOT found")
        return False


def main():
    """Run all dependency checks."""
    print("\n" + "="*60)
    print("Dependency Check - OCR PII Pipeline")
    print("="*60 + "\n")
    
    print("Python Packages:")
    print("-" * 60)
    
    packages = [
        ("opencv-python", "cv2"),
        ("pillow", "PIL"),
        ("numpy", "numpy"),
        ("pytesseract", "pytesseract"),
        ("easyocr", "easyocr"),
        ("spacy", "spacy"),
        ("rapidfuzz", "rapidfuzz"),
        ("matplotlib", "matplotlib"),
        ("pytest", "pytest"),
    ]
    
    results = []
    for pkg_name, import_name in packages:
        results.append(check_package(pkg_name, import_name))
    
    print()
    print("System Dependencies:")
    print("-" * 60)
    
    results.append(check_tesseract())
    results.append(check_spacy_model())
    
    print()
    print("="*60)
    
    total = len(results)
    passed = sum(results)
    
    if passed == total:
        print(f"✓ ALL CHECKS PASSED ({passed}/{total})")
        print("="*60)
        print("\nYou're ready to run the pipeline!")
        print("\nNext step:")
        print("  python run_pipeline.py --input examples/ --output out/ --redact")
        print()
        return True
    else:
        print(f"⚠ SOME CHECKS FAILED ({passed}/{total} passed)")
        print("="*60)
        print("\nTo fix missing dependencies:")
        print("\n1. Install Python packages:")
        print("   pip install -r requirements.txt")
        print("\n2. Download spaCy model:")
        print("   python -m spacy download en_core_web_sm")
        print("\n3. Install Tesseract OCR:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux:   sudo apt-get install tesseract-ocr")
        print("   macOS:   brew install tesseract")
        print("\nOr run automated setup:")
        print("   python setup.py")
        print()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
