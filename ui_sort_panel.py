import tkinter as tk

def create_sort_panel(app):
    """
    ソート条件UI（OptionMenu, Label, trace_add）を生成し、appに必要な変数やイベントをセットする。
    """
    app.sort_key_var = tk.StringVar(value="price")
    app.sort_order_var = tk.StringVar(value="asc")
    frm_sort = tk.Frame(app, bg="#181a1b")
    frm_sort.pack(fill=tk.X, padx=8, pady=(0, 0))
    tk.Label(frm_sort, text="ソート: ", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT)
    opt_sort_key = tk.OptionMenu(frm_sort, app.sort_key_var, "price", "quantity")
    opt_sort_key.config(bg="#23272a", fg="#f5f6fa", highlightbackground="#23272a")
    opt_sort_key.pack(side=tk.LEFT, padx=(0, 8))
    opt_sort_order = tk.OptionMenu(frm_sort, app.sort_order_var, "asc", "desc")
    opt_sort_order.config(bg="#23272a", fg="#f5f6fa", highlightbackground="#23272a")
    opt_sort_order.pack(side=tk.LEFT)
    def on_sort_changed(*_):
        if hasattr(app, "on_sort_changed"):
            app.on_sort_changed()
    app.sort_key_var.trace_add("write", on_sort_changed)
    app.sort_order_var.trace_add("write", on_sort_changed)
