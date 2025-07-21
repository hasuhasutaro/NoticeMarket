# -*- coding: utf-8 -*-
from utils import load_items_json

class OrderConditionManager:
    def __init__(self, search_conditions, excluded_itemids=None):
        self.search_conditions = search_conditions
        self.excluded_itemids = excluded_itemids if excluded_itemids is not None else set()
        self._condition_itemids = []

    def add_condition(self, itemid, min_price, max_price, min_qty, max_qty):
        cond = {
            "min_price": min_price,
            "max_price": max_price,
            "min_quantity": min_qty,
            "max_quantity": max_qty
        }
        self.search_conditions[str(itemid)] = cond

    def del_condition(self, itemid):
        if itemid in self.search_conditions:
            del self.search_conditions[itemid]
            self.excluded_itemids.discard(itemid)

    def exclude_condition(self, itemid):
        if itemid in self.excluded_itemids:
            self.excluded_itemids.remove(itemid)
        else:
            self.excluded_itemids.add(itemid)

    def reload_conditions(self, loader_func):
        self.search_conditions = loader_func()

    def get_condition_list(self):
        items = load_items_json()
        itemid_name_map = {str(item['id']): item['name'] for item in items}
        itemid_tier_map = {str(item['id']): item.get('tier', item.get('itemTier', '?')) for item in items}
        self._condition_itemids = []
        result = []
        for itemid, cond in self.search_conditions.items():
            sid = str(itemid)
            name = itemid_name_map.get(sid, f"(id:{sid})")
            tier = itemid_tier_map.get(sid, '?')
            excluded = " [除外]" if sid in self.excluded_itemids else ""
            # デフォルト値を設定
            min_price = cond.get('min_price', '')
            max_price = cond.get('max_price', '')
            min_quantity = cond.get('min_quantity', '')
            max_quantity = cond.get('max_quantity', '')
            price_range = ""
            if min_price != "" and max_price != "":
                price_range = f"{min_price} <= 価格 <= {max_price}"
            elif min_price != "":
                price_range = f"{min_price} <= 価格"
            elif max_price != "":
                price_range = f"価格 <= {max_price}"
            # 個数
            qty_range = ""
            if min_quantity != "" and max_quantity != "":
                qty_range = f"{min_quantity} <= 個数 <= {max_quantity}"
            elif min_quantity != "":
                qty_range = f"{min_quantity} <= 個数"
            elif max_quantity != "":
                qty_range = f"個数 <= {max_quantity}"
            entry = f"{name} : "
            if price_range:
                entry += f"[ {price_range} ] "
            if qty_range:
                entry += f"[ {qty_range} ]"
            if itemid in self.excluded_itemids:
                entry += " [除外]"
            result.append(entry)
            self._condition_itemids.append(sid)
        return result

    def get_condition_itemids(self):
        return self._condition_itemids
