import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse
import threading
from loguru import logger
import pandas as pd

from common.config import settings
from common.logging_setup import setup_logging
from common.utils import mask_value
from ocr.extract_text import ocr_file
from ai_extraction.gemini_client import extract_structured_data, GeminiError
from ai_extraction.normalize import normalize_ai_output
from parsing.validators import validate_email, validate_phone, validate_postal, parse_date
from parsing.normalizers import title_case_name, normalize_phone, split_address
from datastore.storage import save_record
from ui.preview_table import PreviewTable
from ui.mapping_editor import MappingEditor
from automation.driver import get_driver
from automation.locators import suggest_mapping_for_page
from automation.filler import autofill_with_mapping
from ui.dialogs import show_error, show_info, show_summary

def run_app():
    setup_logging()
    root = tk.Tk()
    root.title(settings.get("app_name", "DocuFill AI"))
    root.geometry("1100x700")

    state = {
        "files": [],
        "extracted_rows": [],
        "table": None,
        "form_url": "",
        "mapping_suggestions": {},
    }

    frm = ttk.Frame(root)
    frm.pack(fill=tk.BOTH, expand=True)

    # Top controls
    top = ttk.Frame(frm)
    top.pack(fill=tk.X, padx=8, pady=6)

    def on_select_files():
        paths = filedialog.askopenfilenames(
            title="Select documents",
            filetypes=[("Docs", "*.pdf *.jpg *.jpeg *.png *.docx"), ("All", "*.*")]
        )
        if paths:
            state["files"] = list(paths)
            show_info(f"Selected {len(paths)} files.")

    def build_rows(flat: dict, src_file: str, page: int, conf: float):
        rows = []
        for k, v in flat.items():
            if k in ("source_file", "page", "confidence", "extraction_method"):
                continue
            rows.append({
                "field": k,
                "value": v or "",
                "confidence": conf,
                "source_file": src_file,
                "page": page
            })
        return rows

    def on_extract():
        if not state["files"]:
            show_error("Please select at least one file.")
            return

        def work():
            rows_all = []
            for f in state["files"]:
                logger.info("OCR: {}", f)
                pages = ocr_file(f)
                for rec in pages:
                    ocr_text = rec["text"]
                    try:
                        ai = extract_structured_data(
                            ocr_text,
                            hints={"form_type": "generic", "priority_fields": ["full_name", "email", "phone"]}
                        )
                    except GeminiError as e:
                        show_error(f"Gemini error: {e}")
                        return
                    flat = normalize_ai_output(ai)
                    flat["source_file"] = rec["source_file"]
                    flat["page"] = rec["page"]
                    conf = float(flat.get("confidence", 0.0))
                    # Post-validate + normalize
                    if flat.get("full_name"):
                        flat["full_name"] = title_case_name(flat["full_name"])
                    if flat.get("phone"):
                        flat["phone"] = normalize_phone(flat["phone"])
                    if flat.get("dob"):
                        date_norm, c = parse_date(flat["dob"])
                        if date_norm:
                            flat["dob"] = date_norm
                    # Heuristic: split address into line1/line2 if combined
                    if not flat.get("address_line1") and flat.get("address_line2"):
                        addr = split_address(flat["address_line2"])
                        flat.update(addr)
                    rows_all.extend(build_rows(flat, rec["source_file"], rec["page"], conf))
            state["extracted_rows"] = rows_all
            refresh_table()

        threading.Thread(target=work, daemon=True).start()

    def refresh_table():
        if state["table"]:
            state["table"].destroy()
            state["table"] = None
        if not state["extracted_rows"]:
            return
        tbl = PreviewTable(frm, state["extracted_rows"])
        tbl.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        state["table"] = tbl

    ttk.Button(top, text="Select Files", command=on_select_files).pack(side=tk.LEFT, padx=4)
    ttk.Button(top, text="Extract (OCR + AI)", command=on_extract).pack(side=tk.LEFT, padx=4)

    url_var = tk.StringVar()
    ttk.Entry(top, textvariable=url_var, width=60).pack(side=tk.LEFT, padx=6)
    ttk.Label(top, text=" Form URL").pack(side=tk.LEFT)

    def on_open_mapping():
        url = url_var.get().strip()
        if not url:
            show_error("Enter a Form URL first.")
            return
        domain = urlparse(url).netloc
        show_info("Opening browser to analyze the page…")
        drv = get_driver()
        try:
            drv.get(url)
            sugg = suggest_mapping_for_page(drv)
            state["mapping_suggestions"] = sugg
            MappingEditor(root, domain, sugg)
        finally:
            drv.quit()

    ttk.Button(top, text="Open Mapping Editor", command=on_open_mapping).pack(side=tk.LEFT, padx=4)

    def on_autofill():
        url = url_var.get().strip()
        if not url:
            show_error("Enter a Form URL first.")
            return
        domain = urlparse(url).netloc
        if not state.get("table"):
            show_error("Nothing to fill. Extract first.")
            return
        data = state["table"].as_dict()
        # Save record locally
        save_record({"domain": domain, "data": data})
        drv = get_driver()
        success, failed = 0, 0
        try:
            drv.get(url)
            # Use latest suggestions (user may have saved profile too)
            success, failed = autofill_with_mapping(drv, domain, data)
        finally:
            drv.quit()
        show_summary(success, failed)

    ttk.Button(top, text="Run Autofill", command=on_autofill).pack(side=tk.LEFT, padx=4)

    root.mainloop()
    return 0
