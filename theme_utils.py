import tkinter as tk
from tkinter import ttk

def set_dark_theme(app):
    style = ttk.Style(app)
    style.theme_use("default")
    style.configure("TLabel", background="#181a1b", foreground="#f5f6fa")
    style.configure("TFrame", background="#181a1b")
    style.configure("TButton", background="#23272a", foreground="#f5f6fa", borderwidth=1)
    style.map("TButton",
        background=[('active', '#2c2f33')],
        foreground=[('active', '#ffffff')]
    )
    style.configure("Treeview",
        background="#23272a",
        foreground="#f5f6fa",
        fieldbackground="#23272a",
        bordercolor="#23272a",
        borderwidth=0,
        rowheight=26
    )
    style.map("Treeview",
        background=[('selected', '#3a3f4b')],
        foreground=[('selected', '#ffffff')]
    )
    style.configure("Treeview.Heading",
        background="#181a1b",
        foreground="#f5f6fa",
        bordercolor="#23272a",
        borderwidth=1
    )
    style.configure("TEntry", fieldbackground="#23272a", foreground="#f5f6fa", background="#23272a")
    style.configure("TCombobox", fieldbackground="#23272a", foreground="#f5f6fa", background="#23272a")
    style.map("TCombobox",
        fieldbackground=[('readonly', '#23272a')],
        foreground=[('readonly', '#f5f6fa')],
        background=[('readonly', '#23272a')]
    )
