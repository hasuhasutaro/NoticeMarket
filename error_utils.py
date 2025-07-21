from tkinter import messagebox
import traceback

def show_error(title, error):
    msg = f"エラーが発生しました:\n{error}\n\n{traceback.format_exc()}"
    try:
        messagebox.showerror(title, msg)
    except Exception:
        print(msg)

# 汎用: show_error("タイトル", Exceptionインスタンス or str)
