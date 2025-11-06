import tkinter as tk
from tkinter import messagebox

def show_error(msg: str):
    messagebox.showerror("Error", msg)

def show_info(msg: str):
    messagebox.showinfo("Info", msg)

def show_summary(success: int, failed: int):
    messagebox.showinfo("Autofill Summary", f"Success: {success}\nFailed: {failed}")
