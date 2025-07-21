import tkinter as tk
import datetime

class TreeViewManager:
    def __init__(self, tree, last_update_var):
        self.tree = tree
        self.last_update_var = last_update_var
        # 色設定（今は固定値、今後constants.pyで管理可能）
        self.bg_colors = ["#23272a", "#181a1b"]

    def update_tree(self, filtered):
        # 最終更新時刻を表示
        now = datetime.datetime.now().strftime("最終更新: %Y-%m-%d %H:%M:%S")
        self.last_update_var.set(now)
        self.tree.delete(*self.tree.get_children())
        last_item_name = None
        color_idx = 0
        for item in filtered:
            place_display = f"(R{item['regionId']}) {item['claimName']}" if 'regionId' in item else item.get('claimName', '')
            item_name = item["itemName"]
            if item_name != last_item_name:
                color_idx = 1 - color_idx
                last_item_name = item_name
            tagname = f"bg{color_idx}"
            rarity = item["itemRarityStr"]
            self.tree.insert("", tk.END, values=(
                item["itemName"], item["itemTier"], item["itemRarityStr"],
                item["priceThreshold"], item["quantity"], place_display
            ), tags=(tagname, f"rarity_{rarity}"))
        self.tree.tag_configure("bg0", background=self.bg_colors[0], foreground="#f5f6fa")
        self.tree.tag_configure("bg1", background=self.bg_colors[1], foreground="#f5f6fa")
        # レアリティごとの色分けは行わず、全体の文字色は白で統一
