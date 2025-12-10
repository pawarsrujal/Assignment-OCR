Assignment-OCR

Automated pipeline for extracting Personal Identifiable Information (PII) from handwritten documents using OCR + post-processing + NLP techniques.

📝 Project Overview

Many institutions and organizations still rely on scanned or handwritten documents for record-keeping. Manually extracting important data (names, addresses, ID numbers, etc.) from such documents is tedious and error-prone. Assignment-OCR aims to automate this task by building an end-to-end pipeline that:

Accepts handwritten document images

Runs pre-processing + OCR to extract raw text

Cleans and normalizes the text

Identifies and extracts PII (names, dates, addresses, identification numbers, etc.)

Outputs cleaned structured data (e.g. JSON or CSV) for further processing

This helps in speeding up data entry, reducing human error, and making PII extraction scalable and reliable.

🚀 Key Features

❇️ Handwritten document support — not just typed or printed text.

🧹 Pre-processing of images — noise removal, normalization, binarization, etc. to improve OCR accuracy.

🔍 OCR + NLP / Named Entity Recognition (NER) — convert images to text, then parse and extract meaningful PII.

📄 Multiple sample inputs supported — test images available (like page_14.jpg, page_30.jpg, etc.) to demonstrate pipeline.

💾 Structured output — extracted PII is stored in a consistent, machine-readable format, usable for downstream tasks (database, CSV, etc.).

📂 Project Structure
assignment-ocr/
│
├── ocr_pii_pipeline/         # main code for processing, OCR, and PII extraction  
├── sample_images/            # sample handwritten document images (e.g. page_14.jpg, page_30.jpg …)  
├── README.md                 # this file  
└── requirements.txt (or equivalent)  # dependencies  


Note: Adjust paths/names depending on your actual folder-naming.

💻 Technology & Dependencies

Language: Python (majority of codebase)

Main dependencies likely include: image processing (e.g. OpenCV or PIL), OCR engine (e.g. Tesseract or similar), NLP / NER libraries (e.g. spaCy, NLTK, or any other)

(Optional) Any additional packages for file I/O, data export (JSON/CSV), logging, etc.

(You should list exact versions/dependencies in requirements.txt or in this section later.)

📥 Installation & Usage

Below is a sample usage flow. Adjust based on your actual code.

# 1. Clone the repo  
git clone https://github.com/your-username/Assignment-OCR.git  
cd Assignment-OCR  

# 2. (Optional) create and activate virtual environment  
python3 -m venv venv  
source venv/bin/activate   # or `venv\Scripts\activate` on Windows  

# 3. Install dependencies  
pip install -r requirements.txt  

# 4. Run the OCR + PII extraction pipeline on a sample image  
python ocr_pii_pipeline/main.py --input sample_images/page_14.jpg --output output.json  


(Modify command-line or config usage based on your actual script parameters.)

🧪 Example / Demo

You may include a small demo using one of the sample images, showing before (handwritten image) → after (structured JSON/CSV output).

For example:

Input: sample_images/page_14.jpg (a handwritten application form)

Output: {"Name": "John Doe", "DateOfBirth": "01-01-1980", "Address": "...", "ID": "ABC12345"}

This showcases medium-to-high accuracy of OCR + PII extraction (depending on handwriting quality).

✅ When to Use This / Use-Cases

Digitizing handwritten records (forms, application sheets, handwritten surveys)

Automating data-entry from hard-copies

Pre-processing for data migration from scanned documents

Sensitive document data extraction (with care for privacy and security)

❗ Known Limitations & Challenges

Handwriting recognition is inherently error-prone — output quality depends heavily on image quality and clarity of handwriting.

OCR + NER errors — mis-recognition or mis-classification of entities may occur.

Not ideal for very messy or stylized handwriting.

PII extraction may require further manual validation for high-stakes use cases (legal, compliance, etc.).

📈 Future Improvements / TODOs

Improve image pre-processing (deskewing, contrast enhancement) to handle noisy images.

Support batch processing of multiple documents.

Add confidence scoring for extracted data.

Integrate human-in-the-loop validation for high-risk PII extraction.

Optionally, wrap pipeline into a web/API service for easier consumption.
