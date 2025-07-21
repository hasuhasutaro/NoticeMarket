import tkinter as tk

class PriceQuantityForm:
    def __init__(self, master):
        self.frame = tk.Frame(master, bg="#181a1b")
        self.frm_priceqty = tk.Frame(self.frame, bg="#181a1b")
        self.frm_priceqty.pack(side=tk.TOP, padx=(0, 8), pady=(25, 0), fill=tk.X)
        self.lbl_price1 = tk.Label(self.frm_priceqty, text="価格 >=", bg="#181a1b", fg="#f5f6fa", width=8, anchor="w")
        self.lbl_price1.grid(row=0, column=0, sticky="w", padx=(0,0), pady=(0,2))
        self.lbl_price2 = tk.Label(self.frm_priceqty, text="価格 <=", bg="#181a1b", fg="#f5f6fa", width=8, anchor="w")
        self.lbl_price2.grid(row=1, column=0, sticky="w", padx=(0,0), pady=(0,2))
        self.lbl_qty1 = tk.Label(self.frm_priceqty, text="個数 >=", bg="#181a1b", fg="#f5f6fa", width=8, anchor="w")
        self.lbl_qty1.grid(row=2, column=0, sticky="w", padx=(0,0), pady=(0,2))
        self.lbl_qty2 = tk.Label(self.frm_priceqty, text="個数 <=", bg="#181a1b", fg="#f5f6fa", width=8, anchor="w")
        self.lbl_qty2.grid(row=3, column=0, sticky="w", padx=(0,0), pady=(0,2))
        self.ent_minprice = tk.Entry(self.frm_priceqty, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_minprice.grid(row=0, column=1, padx=(0,8), pady=(0,2))
        self.ent_maxprice = tk.Entry(self.frm_priceqty, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_maxprice.grid(row=1, column=1, padx=(0,8), pady=(0,2))
        self.ent_minqty = tk.Entry(self.frm_priceqty, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_minqty.grid(row=2, column=1, padx=(0,8), pady=(0,2))
        self.ent_maxqty = tk.Entry(self.frm_priceqty, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_maxqty.grid(row=3, column=1, padx=(0,8), pady=(0,2))

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def get_values(self):
        return {
            "min_price": self.ent_minprice.get(),
            "max_price": self.ent_maxprice.get(),
            "min_qty": self.ent_minqty.get(),
            "max_qty": self.ent_maxqty.get()
        }

    def set_values(self, min_price="", max_price="", min_qty="", max_qty=""):
        self.ent_minprice.delete(0, tk.END)
        self.ent_minprice.insert(0, min_price)
        self.ent_maxprice.delete(0, tk.END)
        self.ent_maxprice.insert(0, max_price)
        self.ent_minqty.delete(0, tk.END)
        self.ent_minqty.insert(0, min_qty)
        self.ent_maxqty.delete(0, tk.END)
        self.ent_maxqty.insert(0, max_qty)
