import io
from pathlib import Path
from typing import Dict, List
import pdfplumber
from PIL import Image
import pytesseract
import cv2
import numpy as np
from common.config import settings
from common.utils import safe_basename
from ocr.preprocess import preprocess_bgr

def _ensure_tesseract_path():
    tpath = settings.get("tesseract_path")
    if tpath:
        pytesseract.pytesseract.tesseract_cmd = tpath

def _ocr_image_pil(pil_img) -> Dict:
    data = pytesseract.image_to_data(pil_img, lang=settings.get("ocr.languages", "eng"),
                                     output_type=pytesseract.Output.DICT)
    text = " ".join([w for w in data.get("text", []) if w and w.strip()])
    confs = [float(c) for c in data.get("conf", []) if c not in ("-1", "")]
    avg_conf = sum(confs) / len(confs) / 100.0 if confs else 0.0
    return {"text": text, "confidence": avg_conf}

def ocr_file(path: str, max_pages: int = None) -> List[Dict]:
    _ensure_tesseract_path()
    p = Path(path)
    out = []
    max_pages = max_pages or settings.get("ocr.max_pages", 50)
    if p.suffix.lower() in [".pdf"]:
        with pdfplumber.open(p) as pdf:
            for idx, page in enumerate(pdf.pages[:max_pages]):
                pil = page.to_image(resolution=settings.get("ocr.dpi_upscale", 300)).original
                bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
                pre = preprocess_bgr(bgr)
                pil2 = Image.fromarray(pre)
                rec = _ocr_image_pil(pil2)
                rec["page"] = idx + 1
                rec["source_file"] = safe_basename(path)
                out.append(rec)
    else:
        pil = Image.open(p)
        bgr = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        pre = preprocess_bgr(bgr)
        pil2 = Image.fromarray(pre)
        rec = _ocr_image_pil(pil2)
        rec["page"] = 1
        rec["source_file"] = safe_basename(path)
        out.append(rec)
    return out
