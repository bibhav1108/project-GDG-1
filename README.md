#  DocuFill AI — Intelligent Document-to-Webform Autofiller

DocuFill AI is a local desktop application that automates the process of *extracting data from documents (PDFs, images, DOCX)* and *auto-filling online forms* such as admission forms, government portals, and institutional websites — all while keeping your data secure on your device.

---

##  Problem Statement

Manual data entry from scanned or digital documents into online forms is *slow, repetitive, and error-prone*  
Institutions, universities, and offices waste valuable time retyping the same details (like name, DOB, email, address, etc.) across multiple portals.

*Challenges faced:*
- Time-consuming manual entry  
- OCR errors and formatting inconsistencies  
- Difficulty mapping document data to form fields  
- Limited accuracy for unlabeled fields  

---

##  Solution Approach

DocuFill AI leverages *OCR (Optical Character Recognition)* and *AI-powered field inference* to automatically detect, extract, and map key information from documents to corresponding form fields.

###  Key Features

-  *Document Ingestion* — Upload PDFs, JPGs, PNGs, or DOCX files.
-  *AI Extraction (OCR + Gemini)* — Extracts structured data like name, DOB, address, email, phone, etc.
-  *Semantic Field Guessing* — Uses Gemini AI to infer unlabeled fields intelligently.
-  *Verification UI* — Edit and verify extracted data in a user-friendly Tkinter table.
-  *Form Autofill* — Automatically fills any online form using Selenium WebDriver (user manually clicks “Submit”).
-  *Privacy First* — All data processed locally; no cloud storage.
-  *Reusable Form Profiles* — Map once, reuse for similar institutional or admission forms.

---

##  Technology Stack

| Component | Technology |
|------------|-------------|
| GUI | Tkinter |
| OCR | Tesseract OCR, pdfplumber, OpenCV |
| AI Inference | Gemini API (models/gemini-1.5-flash-latest) |
| Web Automation | Selenium WebDriver |
| Data Handling | Pandas, JSON, YAML |
| Security | Python Cryptography (Fernet) |
| Configuration | python-dotenv, settings.yaml |
| Logging | Loguru |

---

##  System Architecture Overview

1. **OCR Module (ocr/)**  
   Converts uploaded PDFs or images into readable text using pdfplumber + Tesseract + OpenCV preprocessing.

2. **AI Extraction Module (ai_extraction/)**  
   Sends extracted text to Gemini API for structured JSON output following the canonical schema.

3. **Parsing & Validation (parsing/)**  
   Cleans and validates extracted data (email, phone, postal code, DOB, etc.).

4. **Datastore (datastore/)**  
   Securely saves records locally, supports optional encryption and data masking.

5. **UI Layer (ui/)**  
   Tkinter-based interface for document upload, preview, verification, and webform mapping.

6. **Automation Module (automation/)**  
   Uses Selenium to open a browser, locate form fields, and autofill them based on field mappings.

---

##  Setup / Installation Instructions

### 1 Prerequisites
- *Windows 10/11*
- *Python 3.10+*
- *Tesseract OCR*
  - Download from: https://github.com/UB-Mannheim/tesseract/wiki
  - Default install path: C:\Program Files\Tesseract-OCR\tesseract.exe
- *Chrome Browser + ChromeDriver*
- *Poppler for Windows* (for pdf2image)
  - Download from: https://github.com/oschwartz10612/poppler-windows/releases
  - Add Poppler /bin folder to PATH

### 2 Clone or Download Project
```bash
git clone https://github.com/bibhav1108/project-GDG-1
cd project-GDG-1

The website we are using to implement our prototype 
https://apoorvasrivastava7.github.io/web_form/
