import tkinter as tk
import datetime

class TreeViewManager:
    def __init__(self, tree, last_update_var, items_path="items.json"):
        self.tree = tree
        self.last_update_var = last_update_var
        self.bg_colors = ["#23272a", "#181a1b"]
        import json, os
        self._items_json_cache = None
        self._items_path = items_path

    def get_item_name_by_id(self, itemid):
        import json
        if self._items_json_cache is None:
            try:
                with open(self._items_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._items_json_cache = {str(item["id"]): item.get("name", "") for item in data.get("items", [])}
            except Exception:
                self._items_json_cache = {}
        return self._items_json_cache.get(str(itemid), "")

    def update_tree(self, filtered):
        # 最終更新時刻を表示
        now = datetime.datetime.now().strftime("最終更新: %Y-%m-%d %H:%M:%S")
        self.last_update_var.set(now)
        self.tree.delete(*self.tree.get_children())
        last_item_name = None
        color_idx = 0
        for item in filtered:
            place_display = f"(R{item['regionId']}) {item['claimName']}" if 'regionId' in item else item.get('claimName', '')
            item_name = item.get("itemName")
            if not item_name:
                itemid = item.get("itemId", "")
                item_name = self.get_item_name_by_id(itemid)
            if item_name != last_item_name:
                color_idx = 1 - color_idx
                last_item_name = item_name
            tagname = f"bg{color_idx}"
            rarity = item.get("itemRarityStr", "")
            self.tree.insert("", tk.END, values=(
                item_name,
                item.get("itemTier", ""),
                rarity,
                item.get("priceThreshold", ""),
                item.get("quantity", ""),
                place_display
            ), tags=(tagname, f"rarity_{rarity}"))
        self.tree.tag_configure("bg0", background=self.bg_colors[0], foreground="#f5f6fa")
        self.tree.tag_configure("bg1", background=self.bg_colors[1], foreground="#f5f6fa")
        # レアリティごとの色分けは行わず、全体の文字色は白で統一
