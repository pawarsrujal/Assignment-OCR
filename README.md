# Assignment-OCR
Project Overview: Assignment-OCR
The project, titled "Assignment-OCR," is a specialized application of Optical Character Recognition (OCR) technology, focusing on a critical and sensitive task: the automated extraction of Personal Identifiable Information (PII) from unstructured, handwritten documents.

The core objective is to create a robust and functional pipeline that can successfully process challenging input (handwriting) and accurately identify and extract specific data points that qualify as PII (such as names, addresses, identification numbers, etc.).

#Key Project Aspects (In Points)
1. Core Objective and Challenge
Goal: To build an automated pipeline for PII Extraction from documents.

Primary Challenge: Processing Handwritten Documents, which typically involves lower recognition accuracy and requires more sophisticated pre-processing compared to printed text.

2. Technical Implementation
Project Name: Assignment-OCR

Programming Language: Primarily Python (95.6% of the codebase), suggesting the use of common libraries for image processing, OCR, and Natural Language Processing (NLP) or Named Entity Recognition (NER).

Code Structure: The main implementation is organized within the ocr_pii_pipeline directory. This structure implies a modular approach, likely separating stages like image pre-processing, OCR, and PII identification.

3. Data and Inputs
Input Data Type: Images of documents containing handwritten text.

#Sample Files: The repository includes several sample image files (e.g., page_14.jpg, page_30.jpg), which serve as the test or demonstration data for the pipeline.

Key Document: The file OCR Pipeline Assignment – Handwritten documnet PII Extraction.pdf is the project's definitive requirement and scope document, outlining the specific PII fields to be extracted and any required performance metrics.

4. The OCR Pipeline (Inferred Stages)
The process likely involves the following sequential steps:

Image Pre-processing: Cleaning up the handwritten image (e.g., de-skewing, noise reduction, binarization) to optimize it for OCR.

OCR Execution: Using an OCR engine (e.g., Tesseract, Google Vision API, etc.) to convert the processed image into raw text.

Text Post-processing/Normalization: Cleaning up raw text output, handling OCR errors, and correcting common handwriting recognition mistakes.

PII Identification (NER): Applying advanced text analysis (likely using NLP/NER models) to scan the text and tag specific entities as PII (e.g., names, dates of birth, phone numbers).

Output Generation: Formatting the extracted PII into a structured output (e.g., JSON, CSV, database record) for downstream use.

#Detailed Project Description (In Paragraphs)
The Assignment-OCR project addresses a practical need for automating data entry and compliance from physically written records. Its main focus is on creating an end-to-end pipeline capable of handling one of the most challenging data formats: human handwriting. This mandates the use of cutting-edge computer vision techniques to normalize the input images, thereby maximizing the accuracy of the subsequent OCR engine.

Once the handwritten text is digitized into a raw text string by the OCR component, the project shifts its focus to Personal Identifiable Information (PII) extraction. This step is crucial for sensitive data handling. The pipeline utilizes Python's extensive ecosystem, likely incorporating libraries like OpenCV for image manipulation and a robust NER framework (like spaCy or similar) to accurately locate and categorize various forms of PII. The success of this project is measured not just by the OCR's ability to read the handwriting, but by the pipeline's overall precision and recall in isolating the target PII, a process housed primarily within the ocr_pii_pipeline codebase.
