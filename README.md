🧠 DocuFill AI — Intelligent Document-to-Webform Autofiller

DocuFill AI is a local desktop application that automates the process of extracting structured data (like name, DOB, email, phone, address, etc.) from PDFs, images, and DOCX documents, and auto-filling online forms such as institutional, government, and admission forms — all while keeping your data private and secure on your local device.

🚩 Problem Statement

Manual data entry from scanned or digital documents into online forms is slow, repetitive, and error-prone.
Institutions and offices waste valuable time retyping data such as name, email, and ID across multiple portals.

Challenges faced:

Time-consuming manual entry

Frequent human errors and OCR inconsistencies

Difficulty mapping extracted data to online form fields

Limited AI capability for unlabeled or ambiguous fields

💡 Solution Approach

DocuFill AI uses a hybrid approach combining Tesseract OCR and Gemini AI to intelligently extract and interpret data from documents.
It presents the extracted information in a Tkinter GUI for verification before automatically filling the desired web form using Selenium WebDriver.

✨ Key Features

🧾 Multi-format Upload: Accepts PDFs, JPGs, PNGs, and DOCX files

🤖 AI Extraction (OCR + Gemini): Recognizes and structures key fields

🧠 Smart Field Guessing: Infers unlabeled fields semantically

🧰 Verification Interface: Edit and confirm extracted values before autofill

🌐 Automated Webform Filling: Selenium-based, supports most websites

🔒 Local & Secure: Data never leaves your machine

💾 Reusable Profiles: Save field mappings for specific institutional forms

🧰 Technology Stack
Component	            Technology Used
GUI	                    Tkinter
OCR	              Tesseract OCR, pdfplumber, OpenCV
AI Inference	    Gemini API (gemini-1.5-flash-latest)
Automation	          Selenium WebDriver
Data Handling	      Pandas, JSON, YAML
Security	          Python Cryptography (Fernet)
Config & Env	     python-dotenv, settings.yaml
Logging	                 Loguru


🖥️ System Architecture Overview

OCR Module (ocr/) – Extracts text from PDFs or images using Tesseract and preprocessing filters.

AI Extraction (ai_extraction/) – Uses Gemini API for structured JSON field mapping.

Parsing & Validation (parsing/) – Validates email, phone, DOB, postal codes, etc.

Datastore (datastore/) – Encrypts and securely stores local data.

UI Layer (ui/) – Tkinter-based interface for file upload, preview, and mapping.

Automation (automation/) – Uses Selenium to locate and auto-fill fields in web forms.

⚙️ Setup / Installation Instructions
1️⃣ Prerequisites

Windows 10 or 11

Python 3.10+

Tesseract OCR

Download: Tesseract OCR (UB Mannheim)

Default Path: C:\Program Files\Tesseract-OCR\tesseract.exe

Chrome Browser + ChromeDriver

Poppler for Windows (for PDF support)

Download: Poppler Releases

Add /bin folder to system PATH

2️⃣ Clone or Download the Project
git clone https://github.com/bibhav1108/docufill-ai.git
cd docufill-ai

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment

Create a .env file in the root directory:

GEMINI_API_KEY=your_api_key_here

▶️ How to Run the Project

Launch the app:

python app.py


Upload one or more documents (PDF, JPG, PNG, DOCX).
(Choose the pdf stored in sample/docs folder)

Click “Extract Data” → AI will process and display extracted fields.

Verify and edit the table entries in the preview window.

Enter the target web form URL.
https://apoorvasrivastava7.github.io/web_form/

Click “Auto-Fill Form” → Selenium fills the fields automatically.

Review the log window for success messages or skipped fields.

👥 Team Members
Name	                    Role
Bibhav Upadhyay	  Project Lead / Developer
Shashank Dubey      AI Prompting + PPT
Apoorva Srivastava  web-development(sample_website)

📄 License

This project is open-source for academic and educational use
