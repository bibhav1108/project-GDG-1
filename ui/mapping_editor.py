import tkinter as tk
from tkinter import ttk, messagebox
from urllib.parse import urlparse
from typing import Dict, List
from datastore.storage import save_profile, load_profile

HELP = (
    "Mapping Editor:\n"
    "- Left: Canonical fields.\n"
    "- Right: CSS/XPath selectors of target form inputs.\n"
    "- Use Autofill first: it will propose candidates.\n"
    "- Save to reuse for this site.\n"
)

class MappingEditor(tk.Toplevel):
    def __init__(self, master, domain: str, suggestions: Dict[str, str]):
        super().__init__(master)
        self.title(f"Mapping Editor — {domain}")
        self.geometry("900x520")
        tk.Label(self, text=HELP, justify="left").pack(anchor="w", padx=8, pady=4)
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=("field", "selector"), show="headings")
        self.tree.heading("field", text="Canonical Field")
        self.tree.heading("selector", text="CSS/XPath Selector")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,4), pady=8)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        btns = ttk.Frame(frame)
        btns.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(btns, text="Load Saved", command=lambda: self._load_saved(domain)).pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Save Profile", command=lambda: self._save(domain)).pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Close", command=self.destroy).pack(fill=tk.X, pady=4)

        for k, v in suggestions.items():
            self.tree.insert("", tk.END, values=(k, v))

    def _load_saved(self, domain: str):
        prof = load_profile(domain)
        if not prof:
            messagebox.showinfo("Info", "No saved profile found for this domain.")
            return
        for item in self.tree.get_children(""):
            self.tree.delete(item)
        for k, v in prof.get("mapping", {}).items():
            self.tree.insert("", tk.END, values=(k, v))

    def _save(self, domain: str):
        mapping = {}
        for item in self.tree.get_children(""):
            field, selector = self.tree.item(item)["values"]
            mapping[field] = selector
        save_profile(domain, {"domain": domain, "mapping": mapping})
        messagebox.showinfo("Saved", "Profile saved successfully.")
