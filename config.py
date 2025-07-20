import json
import os

SEARCH_CONDITION_PATH = "search_conditions.json"
SETTINGS_PATH = "settings.json"
DEFAULT_SETTINGS = {"interval_sec": 5, "max_display": 10}

def ensure_settings():
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)

def load_settings():
    ensure_settings()
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
            # デフォルト値補完
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def ensure_search_conditions():
    if not os.path.exists(SEARCH_CONDITION_PATH):
        with open(SEARCH_CONDITION_PATH, "w", encoding="utf-8") as f:
            json.dump({"3210037": {"price": 10000, "color": "red", "min_quantity": 1}}, f, ensure_ascii=False, indent=2)

def load_search_conditions():
    ensure_search_conditions()
    try:
        with open(SEARCH_CONDITION_PATH, encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                if isinstance(v, int):
                    data[k] = {"price": v, "color": "reset", "min_quantity": 1}
                elif isinstance(v, dict) and "min_quantity" not in v:
                    v["min_quantity"] = 1
            return data
    except Exception:
        return {}

def get_market_urls(search_conditions):
    return [f"https://bitjita.com/market/item/{item_id}?hasOrders=true" for item_id in search_conditions.keys()]
