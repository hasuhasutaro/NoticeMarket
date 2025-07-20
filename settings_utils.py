import json
import os

SETTINGS_PATH = "settings.json"
DEFAULT_MAX_DISPLAY = 10

def load_max_display():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_MAX_DISPLAY
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("max_display", DEFAULT_MAX_DISPLAY))
    except Exception:
        return DEFAULT_MAX_DISPLAY

def save_max_display(val):
    # 他の設定値は必ず維持
    data = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    # 既存の値を維持しつつmax_displayだけ上書き
    data["max_display"] = int(val)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
