import sys
__version__ = "2.1.0"
if '--version' in sys.argv:
    print(__version__)
    sys.exit()
# -*- coding: utf-8 -*-
# TODOリファクタ案
# [ ] UI初期化・イベントバインドをsetup_ui等で整理
import tkinter as tk
from tkinter import ttk

import threading
import locale
import queue
import datetime
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox
import os, sys
from api import fetch_market_item
from file_manager import SearchConditionManager
from utils import load_items_json, itemid_to_name_map, item_candidates, extract_itemid_from_candidate
from config import load_settings
from settings_utils import save_max_display, load_max_display
from theme_utils import set_dark_theme

from resource_manager import ResourceManager
from constants import COLUMNS, COLUMN_LABELS, COLUMN_WIDTHS, COLUMN_ANCHORS, BG_COLORS, FG_COLOR

class MarketApp(tk.Tk):
    def on_sort_changed(self):
        # アイテムIDごとにグループ化し、各グループ内でソートして表示
        if hasattr(self, 'filtered_orders'):
            key = self.sort_key_var.get()
            order = self.sort_order_var.get()
            reverse = (order == 'desc')
            from collections import defaultdict
            itemid_groups = defaultdict(list)
            for item in self.filtered_orders:
                itemid = str(item.get('itemId'))
                itemid_groups[itemid].append(item)
            sorted_items = []
            for itemid, group in itemid_groups.items():
                def sort_func(item):
                    if key == 'price':
                        v = float(item.get('priceThreshold', 0))
                    elif key == 'quantity':
                        v = int(item.get('quantity', 0))
                    else:
                        v = 0
                    return v
                group_sorted = sorted(group, key=sort_func, reverse=reverse)
                sorted_items.extend(group_sorted)
            self.treeview_manager.update_tree(sorted_items)
    def on_condition_double_click(self, event):
        self.clear_condition_form()
    def __init__(self):
        super().__init__()
        # items.jsonは初回のみキャッシュ
        self._items_json_cache = None
        self._items_path = "items.json"
        def get_item_data_by_id(itemid):
            import json
            if self._items_json_cache is None:
                try:
                    with open(self._items_path, encoding="utf-8") as f:
                        data = json.load(f)
                        self._items_json_cache = {str(item["id"]): item for item in data.get("items", [])}
                except Exception:
                    self._items_json_cache = {}
            return self._items_json_cache.get(str(itemid), None)
        self.get_item_data_by_id = get_item_data_by_id
        self.itemid_to_data_map = {}
        try:
            import json
            with open("search_conditions.json", encoding="utf-8") as f:
                conds = json.load(f)
                for itemid in conds.keys():
                    item_data = self.get_item_data_by_id(itemid)
                    if item_data:
                        self.itemid_to_data_map[itemid] = item_data
        except Exception:
            pass
        from ui_setup import setup_ui
        setup_ui(self)

    # パネル表示制御はPanelToggleManagerに移譲

    def clear_condition_form(self):
        # 選択解除＆フォームクリア
        self.lst_conditions.selection_clear(0, tk.END)
        self.selected_itemid = None
        self.ent_item.delete(0, tk.END)
        if hasattr(self, 'priceqty_form'):
            self.priceqty_form.set_values("", "", "", "")
        self._last_selected_idx = None

    def on_max_display_changed(self, event=None):
        # Entryの値を直接取得し、空欄なら0にする
        entry_widget = event.widget if event and hasattr(event, 'widget') else None
        if entry_widget:
            val_str = entry_widget.get().strip()
        else:
            val_str = str(self.max_display_var.get()).strip()
        try:
            if val_str == "":
                val = 0
                # Entryウィジェットがあれば0をセット
                if entry_widget:
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, "1")
            else:
                val = int(val_str)
            if val < 0:
                val = 0
            self.settings_manager.set('max_display', val)
        except Exception:
            self.settings_manager.set('max_display', 0)
        # ダブルクリックで選択解除＆フォームクリア
        selection = self.lst_conditions.curselection()
        if not selection:
            return
        self.lst_conditions.selection_clear(0, tk.END)
        self.selected_itemid = None
        self.ent_item.delete(0, tk.END)
        if hasattr(self, 'priceqty_form'):
            self.priceqty_form.set_values("", "", "", "")
        self._last_selected_idx = None

    def on_condition_selected(self, event):
        selection = self.lst_conditions.curselection()
        if not selection:
            self.clear_condition_form()
            return
        idx = selection[0]
        if hasattr(self, '_last_selected_idx') and self._last_selected_idx == idx:
            self.lst_conditions.selection_clear(0, tk.END)
            self.selected_itemid = None
            self.ent_item.delete(0, tk.END)
            self.ent_minprice.delete(0, tk.END)
            self.ent_maxprice.delete(0, tk.END)
            self.ent_minqty.delete(0, tk.END)
            self.ent_maxqty.delete(0, tk.END)
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
            # idから名前取得はitemid_to_data_map参照
            candidate = None
            item_data = self.itemid_to_data_map.get(str(itemid))
            if item_data:
                candidate = item_data.get("name", "")
            if candidate:
                self.ent_item.delete(0, tk.END)
                self.ent_item.insert(0, candidate)
            else:
                self.ent_item.delete(0, tk.END)
            # すべての値を入力欄に反映
            self.ent_minprice.delete(0, tk.END)
            self.ent_minprice.insert(0, cond.get('min_price', ''))
            self.ent_maxprice.delete(0, tk.END)
            self.ent_maxprice.insert(0, cond.get('max_price', ''))
            self.ent_minqty.delete(0, tk.END)
            self.ent_minqty.insert(0, cond.get('min_quantity', ''))
            self.ent_maxqty.delete(0, tk.END)
            self.ent_maxqty.insert(0, cond.get('max_quantity', ''))

    def add_condition(self):
        sel = self.ent_item.get().strip()
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid and sel:
            itemid = self.itemid_map.get(sel)
            if itemid:
                self.selected_itemid = itemid
        # 未入力は空文字、入力があれば整数変換。バリデーションは必須項目のみ。
        def parse_int_or_empty(entry):
            val = entry.get().strip()
            if val == "":
                return ""
            if val.isdigit():
                return int(val)
            messagebox.showerror("入力エラー", f"{entry}は整数で入力してください")
            raise ValueError

        max_price = parse_int_or_empty(self.ent_maxprice)
        min_price = parse_int_or_empty(self.ent_minprice)
        min_qty = parse_int_or_empty(self.ent_minqty)
        max_qty = parse_int_or_empty(self.ent_maxqty)

        if not itemid:
            messagebox.showerror("入力エラー", "アイテム名/IDを選択してください")
            return
        # 条件追加時にitems.jsonからデータ取得してマップに追加
        str_itemid = str(itemid)
        if str_itemid not in self.itemid_to_data_map:
            item_data = self.get_item_data_by_id(str_itemid)
            if item_data:
                self.itemid_to_data_map[str_itemid] = item_data
        # 絞り込み条件に全て渡す（引数順: min_price, max_price, min_qty, max_qty）
        self.condition_manager.add_condition(itemid, min_price, max_price, min_qty, max_qty)
        # SearchConditionManagerで保存
        if hasattr(self, 'search_cond_manager'):
            self.search_cond_manager.save_conditions(self.search_conditions)
        self.update_condition_listbox()

    def del_condition(self):
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid:
            sel = self.ent_item.get().strip()
            itemid = self.itemid_map.get(sel)
        if not itemid:
            return
        itemid = str(itemid)
        self.condition_manager.del_condition(itemid)
        if hasattr(self, 'search_cond_manager'):
            self.search_cond_manager.save_conditions(self.search_conditions)
        self.selected_itemid = None
        self.lst_conditions.selection_clear(0, tk.END)
        self.update_condition_listbox()

    def reload_conditions(self):
        if hasattr(self, 'search_cond_manager'):
            self.condition_manager.reload_conditions(self.search_cond_manager.load_conditions)
        self.update_condition_listbox()

    def update_condition_listbox(self):
        self.lst_conditions.delete(0, tk.END)
        cond_list = self.condition_manager.get_condition_list()
        self._condition_itemids = self.condition_manager.get_condition_itemids()
        for entry in cond_list:
            self.lst_conditions.insert(tk.END, entry)
    def exclude_condition(self):
        itemid = getattr(self, 'selected_itemid', None)
        if not itemid:
            sel = self.ent_item.get().strip()
            itemid = self.itemid_map.get(sel)
        if not itemid:
            return
        itemid = str(itemid)
        self.condition_manager.exclude_condition(itemid)
        self.update_condition_listbox()

    def update_market(self):
        # OrderFetcherにAPI取得・整形・エラーハンドリングを委譲
        from order_fetcher import OrderFetcher
        from error_utils import show_error
        def on_market_fetched(filtered):
            self.filtered_orders = filtered
            self.after(0, self.on_sort_changed)
        def run_fetch():
            try:
                order_fetcher = OrderFetcher(fetch_market_item, order_key="sellOrders")
                cond_items = list(self.search_conditions.items())
                max_display = self.max_display_var.get()
                if str(max_display).strip() == "":
                    max_display = 0
                else:
                    max_display = int(max_display)
                filtered = order_fetcher.fetch_orders(
                    cond_items,
                    self.excluded_itemids,
                    max_display
                )
                self.filtered_orders = filtered
                on_market_fetched(filtered)
            except Exception as e:
                show_error("マーケット情報取得エラー", e)
        threading.Thread(target=run_fetch, daemon=True).start()
        interval_sec = self.settings.get('interval_sec', 2)
        self.after(int(interval_sec * 1000), self.update_market)

    # fetch_and_display_marketはOrderFetcherに一元化したため削除

    def update_tree(self, filtered):
        # TreeViewManagerに委譲
        self.treeview_manager.update_tree(filtered)

from ensure_items_json import ensure_items_json

if __name__ == "__main__":
    ensure_items_json()
    app = MarketApp()
    app.mainloop()
