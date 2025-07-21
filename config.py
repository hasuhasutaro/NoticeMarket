import json
import os

SETTINGS_PATH = "settings.json"
DEFAULT_SETTINGS = {"interval_sec": 10, "max_display": 10}

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


def get_market_urls(search_conditions):
    return [f"https://bitjita.com/market/item/{item_id}?hasOrders=true" for item_id in search_conditions.keys()]
