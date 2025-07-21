# -*- coding: utf-8 -*-
import threading
import queue
from collections import defaultdict

class OrderFetcher:
    def __init__(self, fetch_func, order_key):
        """
        fetch_func: 条件ごとにAPIを叩く関数 (例: fetch_market_item)
        order_key: APIレスポンスのキー ('sellOrders' or 'buyOrders')
        """
        self.fetch_func = fetch_func
        self.order_key = order_key

    def fetch_orders(self, cond_items, excluded_itemids, max_display_var):
        """
        cond_items: [(itemid, cond)] のリスト
        excluded_itemids: 除外itemidのset
        max_display_var: 最大表示件数 (int)
        return: フィルタ済みorderリスト
        """
        q = queue.Queue()
        threads = []
        # 除外されていない条件のみ取得
        cond_items = [(cid, cond) for cid, cond in cond_items if str(cid) not in excluded_itemids]

        def fetch_worker(cond_id, cond):
            try:
                data = self.fetch_func(cond_id)
                items = data.get(self.order_key, [])
                for item in items:
                    try:
                        price_raw = item.get("priceThreshold")
                        quantity_raw = item.get("quantity")
                        price = float(price_raw) if price_raw not in (None, "") else 0
                        quantity = int(quantity_raw) if quantity_raw not in (None, "") else 0
                        # 未入力値はフィルタ条件に使わない
                        min_price_raw = cond.get("min_price", None)
                        max_price_raw = cond.get("max_price", None)
                        min_quantity_raw = cond.get("min_quantity", None)
                        max_quantity_raw = cond.get("max_quantity", None)

                        passed = True
                        if min_price_raw not in (None, ""):
                            try:
                                min_price = float(min_price_raw)
                                if price < min_price:
                                    passed = False
                            except Exception:
                                pass
                        if max_price_raw not in (None, ""):
                            try:
                                max_price = float(max_price_raw)
                                if price > max_price:
                                    passed = False
                            except Exception:
                                pass
                        if min_quantity_raw not in (None, ""):
                            try:
                                min_quantity = int(min_quantity_raw)
                                if quantity < min_quantity:
                                    passed = False
                            except Exception:
                                pass
                        if max_quantity_raw not in (None, ""):
                            try:
                                max_quantity = int(max_quantity_raw)
                                if quantity > max_quantity:
                                    passed = False
                            except Exception:
                                pass
                        if passed:
                            q.put(item)
                    except Exception:
                        pass
            except Exception:
                pass

        for cond_id, cond in cond_items:
            t = threading.Thread(target=fetch_worker, args=(cond_id, cond))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        all_items = []
        while not q.empty():
            all_items.append(q.get())

        # itemIdごとにまとめて、アイテム名→価格→数量の順でソートし、条件順・最大件数で表示
        max_per_item = max_display_var
        itemid_to_items = defaultdict(list)
        for item in all_items:
            itemid = str(item.get("itemId"))
            itemid_to_items[itemid].append(item)

        filtered = []
        for cond_id, _ in cond_items:
            items = itemid_to_items.get(str(cond_id), [])
            items.sort(key=lambda x: (
                x.get("itemName", ""),
                float(x.get("priceThreshold", 0)),
                -int(x.get("quantity", 0))
            ))
            filtered.extend(items[:max_per_item])
        return filtered
