import os
import sys
import locale
import json

def resource_path(rel_path):
    locale.setlocale(locale.LC_CTYPE, 'Japanese_Japan.932')
    if getattr(sys, 'frozen', False):
        # .exeで実行中（PyInstaller）
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel_path)

class SettingsManager:
    def __init__(self, settings_path=None):
        self.settings_path = settings_path or resource_path('settings.json')
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_settings(self, settings):
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        self.settings = settings

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)

class SearchConditionManager:
    def __init__(self, cond_path=None):
        self.cond_path = cond_path or resource_path('search_conditions.json')
        self.conditions = self.load_conditions()

    def load_conditions(self):
        try:
            with open(self.cond_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_conditions(self, conditions):
        with open(self.cond_path, 'w', encoding='utf-8') as f:
            json.dump(conditions, f, ensure_ascii=False, indent=2)
        self.conditions = conditions

    def get(self, itemid):
        return self.conditions.get(itemid)

    def set(self, itemid, cond):
        self.conditions[itemid] = cond
        self.save_conditions(self.conditions)

    def delete(self, itemid):
        if itemid in self.conditions:
            del self.conditions[itemid]
            self.save_conditions(self.conditions)

    def all(self):
        return self.conditions
