from typing import List, Dict
import tkinter as tk
from tkinter import ttk
from common.config import settings

def _confidence_tag(conf: float) -> str:
    hi = settings.get("ui.table_confidence_thresholds.high", 0.85)
    mid = settings.get("ui.table_confidence_thresholds.medium", 0.6)
    if conf >= hi:
        return "high"
    if conf >= mid:
        return "medium"
    return "low"

class PreviewTable(ttk.Frame):
    def __init__(self, master, rows: List[Dict]):
        super().__init__(master)
        self.tree = ttk.Treeview(self, columns=("field", "value", "confidence"), show="headings")
        self.tree.heading("field", text="Field")
        self.tree.heading("value", text="Value (double-click to edit)")
        self.tree.heading("confidence", text="Conf.")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.tag_configure("high", background="#E7F7E7")
        self.tree.tag_configure("medium", background="#FFF8E1")
        self.tree.tag_configure("low", background="#FFEAEA")
        self._rows = rows
        self._populate()
        self.tree.bind("<Double-1>", self._on_edit)

    def _populate(self):
        for r in self._rows:
            tag = _confidence_tag(float(r.get("confidence", 0.0)))
            self.tree.insert("", tk.END, values=(r["field"], r["value"], f'{r.get("confidence", 0):.2f}'),
                             tags=(tag,))

    def _on_edit(self, event):
        item = self.tree.focus()
        if not item:
            return
        col = self.tree.identify_column(event.x)
        if col != "#2":
            return
        x, y, w, h = self.tree.bbox(item, column=1)
        value = self.tree.set(item, "value")
        editor = tk.Entry(self.tree)
        editor.insert(0, value)
        editor.place(x=x, y=y, width=w, height=h)
        editor.focus_set()

        def on_enter(_):
            new_val = editor.get()
            self.tree.set(item, "value", new_val)
            editor.destroy()

        def on_focus_out(_):
            editor.destroy()

        editor.bind("<Return>", on_enter)
        editor.bind("<FocusOut>", on_focus_out)

    def as_dict(self) -> Dict[str, str]:
        out = {}
        for item in self.tree.get_children(""):
            field, value, _ = self.tree.item(item)["values"]
            out[field] = value
        return out
