import json
import os

SEARCH_CONDITIONS_PATH = "search_conditions.json"

def load_search_conditions():
    if not os.path.exists(SEARCH_CONDITIONS_PATH):
        return {}
    with open(SEARCH_CONDITIONS_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_search_conditions(conditions):
    with open(SEARCH_CONDITIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(conditions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # テスト用: サンプル条件の保存と読み込み
    sample = {
        "3210037": {"max_price": 10, "min_quantity": 5},
        "2097987865": {"max_price": 75, "min_quantity": 10}
    }
    save_search_conditions(sample)
    print(load_search_conditions())
