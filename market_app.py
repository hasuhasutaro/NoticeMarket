# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

import threading
import locale
import queue
import datetime
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox
import os, sys
def resource_path(rel_path):
    locale.setlocale(locale.LC_CTYPE, 'Japanese_Japan.932')  # システムデフォルトロケール（日本語Windowsなら日本語）
    # exe/pyどちらでも実行ファイルのあるディレクトリ基準でパスを返す
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel_path)
from api import fetch_market_item
from search_conditions import load_search_conditions, save_search_conditions
from utils import load_items_json, itemid_to_name_map, item_candidates, extract_itemid_from_candidate
from config import load_settings
from settings_utils import save_max_display, load_max_display

class MarketApp(tk.Tk):
    def on_condition_double_click(self, event):
        self.clear_condition_form()
    def __init__(self):
        super().__init__()
        self.title("マーケット情報 - NotificationMarket")
        self.geometry("1100x600")
        self.configure(bg="#181a1b")  # ダーク背景
        # 設定・条件ファイルは従来通り引数なしで呼び出し
        self.settings = load_settings()
        self.search_conditions = load_search_conditions()
        self.excluded_itemids = set()  # 一時除外中のitemid
        self.last_update_var = tk.StringVar()
        self.max_display_var = tk.IntVar(value=load_max_display())
        self.style = ttk.Style(self)
        self.set_dark_theme()
        # UI部品を直接作成
        columns = ("itemName", "itemTier", "itemRarityStr", "priceThreshold", "quantity", "regionName")
        # 最終更新時刻ラベル（テーブル左上に表示）
        self.lbl_last_update = tk.Label(self, textvariable=self.last_update_var, anchor="w", bg="#181a1b", fg="#f5f6fa")
        self.lbl_last_update.pack(anchor="nw", padx=8, pady=(8,0))
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="Treeview")
        self.tree.heading("itemName", text="アイテム名")
        self.tree.heading("itemTier", text="Tier")
        self.tree.heading("itemRarityStr", text="レア度")
        self.tree.heading("priceThreshold", text="価格")
        self.tree.heading("quantity", text="数量")
        self.tree.heading("regionName", text="場所")
        self.tree.column("itemName", width=260)
        self.tree.column("itemTier", width=50, anchor="center")
        self.tree.column("itemRarityStr", width=80, anchor="center")
        self.tree.column("priceThreshold", width=70, anchor="e")
        self.tree.column("quantity", width=70, anchor="e")
        self.tree.column("regionName", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 横一列に並べるフレーム
        self.frm_top = tk.Frame(self, bg="#181a1b")
        self.frm_top.pack(pady=4, fill=tk.X)
        # 最大件数
        tk.Label(self.frm_top, text="最大件数", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
        ent_maxdisp = tk.Entry(self.frm_top, textvariable=self.max_display_var, width=5, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        ent_maxdisp.pack(side=tk.LEFT, padx=(0, 8))
        ent_maxdisp.bind("<FocusOut>", self.on_max_display_changed)
        ent_maxdisp.bind("<Return>", self.on_max_display_changed)
        # アイテム名
        tk.Label(self.frm_top, text="アイテム名/ID", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
        items = load_items_json()
        # サジェスト候補を「アイテム名 (TierX/レア度) (itemid)」形式に
        self.item_candidates = [
            f"{item['name']} (Tier{item.get('tier', item.get('itemTier', '?'))}/{item.get('rarity', item.get('itemRarityStr', '?'))}) ({item['id']})"
            for item in items
        ]
        # itemid_mapも新しい形式に合わせて修正
        import re
        def extract_itemid(candidate):
            m = re.search(r'\((\d+)\)$', candidate)
            return m.group(1) if m else ''
        self.itemid_map = {c: extract_itemid(c) for c in self.item_candidates}

        # --- 入力欄を左から順に整列 ---
        tk.Label(self.frm_top, text="アイテム名/ID", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
        self.ent_item = tk.Entry(self.frm_top, width=40, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_item.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(self.frm_top, text="最大価格", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
        self.ent_maxprice = tk.Entry(self.frm_top, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_maxprice.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(self.frm_top, text="最小個数", bg="#181a1b", fg="#f5f6fa").pack(side=tk.LEFT, padx=(0, 2))
        self.ent_minqty = tk.Entry(self.frm_top, width=10, bg="#23272a", fg="#f5f6fa", insertbackground="#f5f6fa")
        self.ent_minqty.pack(side=tk.LEFT, padx=(0, 8))
        btn_add = tk.Button(self.frm_top, text="条件追加", command=self.add_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        btn_add.pack(side=tk.LEFT, padx=(0, 4))
        btn_del = tk.Button(self.frm_top, text="条件削除", command=self.del_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        btn_del.pack(side=tk.LEFT, padx=(0, 4))
        btn_exclude = tk.Button(self.frm_top, text="一時除外", command=self.exclude_condition, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        btn_exclude.pack(side=tk.LEFT, padx=(0, 4))
        btn_clear = tk.Button(self.frm_top, text="選択解除", command=self.clear_condition_form, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        btn_clear.pack(side=tk.LEFT, padx=(0, 4))
        btn_reload = tk.Button(self.frm_top, text="検索条件リロード", command=self.reload_conditions, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        btn_reload.pack(side=tk.LEFT, padx=(0, 4))

        # --- 条件一覧下部、サジェストListBoxを右側に横並びで配置 ---
        self.frm_condition = tk.Frame(self, bg="#181a1b")
        self.frm_condition.pack(pady=4)
        self.lst_conditions = tk.Listbox(self.frm_condition, width=80, height=6, bg="#23272a", fg="#f5f6fa", selectbackground="#3a3f4b", selectforeground="#ffffff", highlightbackground="#23272a", highlightcolor="#23272a")
        self.lst_conditions.pack(side=tk.RIGHT, padx=4, pady=4)
        self.lst_conditions.bind("<<ListboxSelect>>", self.on_condition_selected)
        self.lst_conditions.bind("<Double-Button-1>", self.on_condition_double_click)
        self.listbox_suggest = tk.Listbox(self.frm_condition, width=40, height=6, bg="#23272a", fg="#f5f6fa", selectbackground="#3a3f4b", selectforeground="#ffffff", highlightbackground="#23272a", highlightcolor="#23272a")
        self.listbox_suggest.pack(side=tk.LEFT, padx=(125,4), pady=4)

        import threading
        self._suggest_thread = None
        self._suggest_cancel = threading.Event()

        def update_suggest_list(event=None):
            # 前回スレッドがあればキャンセル
            if self._suggest_thread and self._suggest_thread.is_alive():
                self._suggest_cancel.set()
                self._suggest_thread.join(timeout=0.1)
            self._suggest_cancel.clear()
            current = self.ent_item.get()
            words = [w for w in current.lower().split() if w]
            all_values = self.item_candidates[:]
            def worker():
                if words:
                    filtered = [v for v in all_values if all(word in v.lower() for word in words)]
                    def sort_key(v):
                        v_lower = v.lower()
                        joined = " ".join(words)
                        if v_lower == joined:
                            return (0, 0, v_lower)
                        if all(v_lower.find(word) == 0 for word in words):
                            return (1, 0, v_lower)
                        if all(word in v_lower for word in words):
                            total_idx = sum(v_lower.find(word) for word in words)
                            return (2, total_idx, v_lower)
                        return (3, 9999, v_lower)
                    values = sorted(filtered, key=sort_key)
                else:
                    values = all_values
                # キャンセルされていれば何もしない
                if self._suggest_cancel.is_set():
                    return
                def update_listbox():
                    self.listbox_suggest.delete(0, tk.END)
                    for v in values:
                        self.listbox_suggest.insert(tk.END, v)
                self.after(0, update_listbox)
            self._suggest_thread = threading.Thread(target=worker, daemon=True)
            self._suggest_thread.start()

        def on_suggest_select(event):
            if self.listbox_suggest.curselection():
                val = self.listbox_suggest.get(self.listbox_suggest.curselection()[0])
                self.ent_item.delete(0, tk.END)
                self.ent_item.insert(0, val)
                # itemidもセット
                self.selected_itemid = self.itemid_map.get(val, "")

        self.ent_item.bind('<KeyRelease>', update_suggest_list)
        self.listbox_suggest.bind('<<ListboxSelect>>', on_suggest_select)
        self.listbox_suggest.bind('<ButtonRelease-1>', on_suggest_select)


        # トグルボタン（ウィンドウ下部に移動）
        self.btn_toggle_condition = tk.Button(self, text="条件パネル非表示", command=self.toggle_condition_panel, bg="#23272a", fg="#f5f6fa", activebackground="#2c2f33", activeforeground="#ffffff")
        self.btn_toggle_condition.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        self.after(0, self.update_market)

        # 検索条件一覧を初期表示
        self.update_condition_listbox()

    def toggle_condition_panel(self):
        # frm_top(最大件数)とfrm_condition(条件パネル)を同時にトグル
        if self.frm_condition.winfo_ismapped() or self.frm_top.winfo_ismapped():
            self.frm_condition.pack_forget()
            self.frm_top.pack_forget()
            self.btn_toggle_condition.config(text="条件パネル表示")
        else:
            self.frm_top.pack(pady=4)
            self.frm_condition.pack(pady=4)
            self.btn_toggle_condition.config(text="条件パネル非表示")

    def set_dark_theme(self):
        # ttkテーマをダーク系にカスタマイズ
        self.style.theme_use("default")
        self.style.configure("TLabel", background="#181a1b", foreground="#f5f6fa")
        self.style.configure("TFrame", background="#181a1b")
        self.style.configure("TButton", background="#23272a", foreground="#f5f6fa", borderwidth=1)
        self.style.map("TButton",
            background=[('active', '#2c2f33')],
            foreground=[('active', '#ffffff')]
        )
        self.style.configure("Treeview",
            background="#23272a",
            foreground="#f5f6fa",
            fieldbackground="#23272a",
            bordercolor="#23272a",
            borderwidth=0,
            rowheight=26
        )
        self.style.map("Treeview",
            background=[('selected', '#3a3f4b')],
            foreground=[('selected', '#ffffff')]
        )
        self.style.configure("Treeview.Heading",
            background="#181a1b",
            foreground="#f5f6fa",
            bordercolor="#23272a",
            borderwidth=1
        )
        self.style.configure("TEntry", fieldbackground="#23272a", foreground="#f5f6fa", background="#23272a")
        self.style.configure("TCombobox", fieldbackground="#23272a", foreground="#f5f6fa", background="#23272a")
        self.style.map("TCombobox",
            fieldbackground=[('readonly', '#23272a')],
            foreground=[('readonly', '#f5f6fa')],
            background=[('readonly', '#23272a')]
        )


    def clear_condition_form(self):
        # 選択解除＆フォームクリア
        self.lst_conditions.selection_clear(0, tk.END)
        self.selected_itemid = None
        self.ent_item.delete(0, tk.END)
        self.ent_maxprice.delete(0, tk.END)
        self.ent_minqty.delete(0, tk.END)
        self._last_selected_idx = None

    def on_max_display_changed(self, event=None):
        # Entryの値をsettings.jsonに保存（バリデーションのみ）
        try:
            val = int(self.max_display_var.get())
            if val < 1:
                raise ValueError
            save_max_display(val)
        except Exception:
            # 不正値なら元に戻す
            save_max_display(val)
        # ダブルクリックで選択解除＆フォームクリア
        selection = self.lst_conditions.curselection()
        if not selection:
            return
        self.lst_conditions.selection_clear(0, tk.END)
        self.selected_itemid = None
        self.ent_item.delete(0, tk.END)
        self.ent_maxprice.delete(0, tk.END)
        self.ent_minqty.delete(0, tk.END)
        self._last_selected_idx = None

    def on_condition_selected(self, event):
        selection = self.lst_conditions.curselection()
        if not selection:
            self.selected_itemid = None
            self._last_selected_idx = None
            return
        idx = selection[0]
        if hasattr(self, '_last_selected_idx') and self._last_selected_idx == idx:
            self.lst_conditions.selection_clear(0, tk.END)
            self.selected_itemid = None
            self.ent_item.delete(0, tk.END)
            self.ent_maxprice.delete(0, tk.END)
            self.ent_minqty.delete(0, tk.END)
            self._last_selected_idx = None
            return
        self._last_selected_idx = idx
        # 裏で持っているitemidリストから取得
        if hasattr(self, '_condition_itemids') and idx < len(self._condition_itemids):
            itemid = self._condition_itemids[idx]
        else:
            itemid = None
        self.selected_itemid = itemid
        if itemid and itemid in self.search_conditions:
            cond = self.search_conditions[itemid]
            candidate = None
            for c in self.item_candidates:
                if self.itemid_map.get(c) == itemid:
                    candidate = c
                    break
            if candidate:
                self.ent_item.delete(0, tk.END)
                self.ent_item.insert(0, candidate)
            else:
                self.ent_item.delete(0, tk.END)
            self.ent_maxprice.delete(0, tk.END)
            self.ent_maxprice.insert(0, cond.get('max_price', ''))
            self.ent_minqty.delete(0, tk.END)
            self.ent_minqty.insert(0, cond.get('min_quantity', ''))

    # on_combobox_keyreleaseは不要



    def add_condition(self):
        # 入力値が候補に完全一致していればitemidを自動取得
        sel = self.ent_item.get().strip()
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid and sel:
            # 候補リストから完全一致を探す
            itemid = self.itemid_map.get(sel)
            if itemid:
                self.selected_itemid = itemid
        try:
            max_price = int(self.ent_maxprice.get())
            min_qty = int(self.ent_minqty.get())
        except ValueError:
            messagebox.showerror("入力エラー", "最大価格・最小個数は整数で入力してください")
            return
        # 最大価格・最小個数は整数のみ許可
        if not self.ent_maxprice.get().strip().isdigit():
            messagebox.showerror("入力エラー", "最大価格は整数で入力してください")
            return
        if not self.ent_minqty.get().strip().isdigit():
            messagebox.showerror("入力エラー", "最小個数は整数で入力してください")
            return
        if not itemid:
            messagebox.showerror("入力エラー", "アイテム名/IDを選択してください")
            return
        self.search_conditions[itemid] = {"max_price": max_price, "min_quantity": min_qty}
        save_search_conditions(self.search_conditions)
        self.update_condition_listbox()

    def del_condition(self):
        # 条件一覧で選択されたitemIdまたは入力欄で選択されたitemIdを優先
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid:
            sel = self.ent_item.get().strip()
            itemid = self.itemid_map.get(sel)
        if not itemid:
            return
        itemid = str(itemid)
        if itemid in self.search_conditions:
            del self.search_conditions[itemid]
            save_search_conditions(self.search_conditions)
            self.selected_itemid = None
            self.lst_conditions.selection_clear(0, tk.END)
            self.update_condition_listbox()

    def reload_conditions(self):
        self.search_conditions = load_search_conditions()
        self.update_condition_listbox()

    def update_condition_listbox(self):
        self.lst_conditions.delete(0, tk.END)
        items = load_items_json()
        itemid_name_map = {str(item['id']): item['name'] for item in items}
        itemid_tier_map = {str(item['id']): item.get('tier', item.get('itemTier', '?')) for item in items}
        self._condition_itemids = []  # itemidのリストを裏で持つ
        for itemid, cond in self.search_conditions.items():
            sid = str(itemid)
            name = itemid_name_map.get(sid, f"(id:{sid})")
            tier = itemid_tier_map.get(sid, '?')
            excluded = " [除外]" if sid in self.excluded_itemids else ""
            self.lst_conditions.insert(
                tk.END,
                f"{name} (Tier{tier}) / 最大価格: {cond.get('max_price')} / 最小個数: {cond.get('min_quantity')}{excluded}"
            )
            self._condition_itemids.append(sid)
    def exclude_condition(self):
        # 条件一覧で選択されたitemIdまたは入力欄で選択されたitemIdを一時除外/解除
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid:
            sel = self.ent_item.get().strip()
            itemid = self.itemid_map.get(sel)
        if not itemid:
            return
        itemid = str(itemid)
        if itemid in self.excluded_itemids:
            self.excluded_itemids.remove(itemid)
        else:
            self.excluded_itemids.add(itemid)
        self.update_condition_listbox()

    def update_market(self):
        def run_with_error_popup():
            try:
                self.fetch_and_display_market()
            except Exception as e:
                import traceback
                msg = f"エラーが発生しました:\n{e}\n\n{traceback.format_exc()}"
                try:
                    messagebox.showerror("エラー", msg)
                except Exception:
                    print(msg)
        threading.Thread(target=run_with_error_popup, daemon=True).start()
        # 設定値 interval_sec を使う
        interval_sec = self.settings.get('interval_sec', 2)
        self.after(int(interval_sec * 1000), self.update_market)

    def fetch_and_display_market(self):
        try:
            itemid_name_map = itemid_to_name_map()
            filtered = []
            q = queue.Queue()
            threads = []
            # 除外されていない条件のみ取得
            cond_items = [(cid, cond) for cid, cond in self.search_conditions.items() if str(cid) not in self.excluded_itemids]

            def fetch_worker(cond_id, cond):
                try:
                    data = fetch_market_item(cond_id)
                    items = data.get("sellOrders", [])
                    for item in items:
                        try:
                            price_raw = item.get("priceThreshold")
                            quantity_raw = item.get("quantity")
                            price = float(price_raw) if price_raw not in (None, "") else 0
                            quantity = int(quantity_raw) if quantity_raw not in (None, "") else 0
                            max_price = float(cond.get("max_price", float("inf")))
                            min_quantity = int(cond.get("min_quantity", 0))
                            if price <= max_price and quantity >= min_quantity:
                                q.put(item)
                        except Exception:
                            pass
                except Exception as e:
                    import traceback
                    msg = f"API取得エラー: {e}\n{traceback.format_exc()}"
                    try:
                        messagebox.showerror("API取得エラー", msg)
                    except Exception:
                        print(msg)

            # 並列で全条件取得
            for cond_id, cond in cond_items:
                t = threading.Thread(target=fetch_worker, args=(cond_id, cond))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

            # queueから全件取得
            all_items = []
            while not q.empty():
                all_items.append(q.get())

            # itemIdごとにまとめて、アイテム名→価格→数量の順でソートし、条件順・最大件数で表示
            max_per_item = self.max_display_var.get()
            from collections import defaultdict
            itemid_to_items = defaultdict(list)
            for item in all_items:
                itemid = str(item.get("itemId"))
                itemid_to_items[itemid].append(item)

            filtered = []
            for cond_id, _ in cond_items:
                items = itemid_to_items.get(str(cond_id), [])
                # アイテム名→価格→数量の順でソート
                items.sort(key=lambda x: (
                    x.get("itemName", ""),
                    float(x.get("priceThreshold", 0)),
                    -int(x.get("quantity", 0))
                ))
                filtered.extend(items[:max_per_item])

            # メインスレッドでGUI更新
            self.after(0, lambda: self.update_tree(filtered))
        except Exception as e:
            import traceback
            msg = f"マーケット情報取得エラー: {e}\n{traceback.format_exc()}"
            try:
                messagebox.showerror("マーケット情報取得エラー", msg)
            except Exception:
                print(msg)

    def update_tree(self, filtered):
        # 最終更新時刻を表示
        now = datetime.datetime.now().strftime("最終更新: %Y-%m-%d %H:%M:%S")
        self.last_update_var.set(now)
        # ソート済みなのでここでのソートは不要
        self.tree.delete(*self.tree.get_children())
        # アイテム名ごとに背景色を交互に変える（ダーク基調）
        bg_colors = ["#23272a", "#181a1b"]  # ダークグレーとさらに濃いグレー
        last_item_name = None
        color_idx = 0
        for item in filtered:
            place_display = f"(R{item['regionId']}) {item['claimName']}" if 'regionId' in item else item.get('claimName', '')
            item_name = item["itemName"]
            if item_name != last_item_name:
                color_idx = 1 - color_idx  # 交互に切り替え
                last_item_name = item_name
            tagname = f"bg{color_idx}"
            rarity = item["itemRarityStr"]
            iid = self.tree.insert("", tk.END, values=(
                item["itemName"], item["itemTier"], item["itemRarityStr"],
                item["priceThreshold"], item["quantity"], place_display
            ), tags=(tagname, f"rarity_{rarity}"))
        # 背景色タグ設定・全体の文字色は白
        self.tree.tag_configure("bg0", background=bg_colors[0], foreground="#f5f6fa")
        self.tree.tag_configure("bg1", background=bg_colors[1], foreground="#f5f6fa")
        # レアリティごとの色分けは行わず、全体の文字色は白で統一

from ensure_items_json import ensure_items_json

if __name__ == "__main__":
    ensure_items_json()
    app = MarketApp()
    app.mainloop()
