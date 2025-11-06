# DocuFill AI — Local Document → Webform Autofill (Windows)

**Local-first. Private. Beginner-friendly.**  
Extract data from PDFs/Images/DOCX with Tesseract + Gemini, review in a table, and auto-fill any web form with Selenium.

## One-command setup (Windows)

1) Install Python 3.10–3.12 (x64)  
2) Install Tesseract OCR (Windows installer):  
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Note the install path, e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`
3) Clone project and open terminal in the project root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
"# project-GDG" 
