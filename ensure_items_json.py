import os
import json
from api import fetch_items

ITEMS_JSON_PATH = "items.json"

def ensure_items_json():
    """
    items.jsonがなければAPIから取得して保存する
    """
    if not os.path.exists(ITEMS_JSON_PATH):
        data = fetch_items()
        with open(ITEMS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    return False

if __name__ == "__main__":
    created = ensure_items_json()
    if created:
        print("items.jsonを新規作成しました。")
    else:
        print("items.jsonは既に存在します。")
