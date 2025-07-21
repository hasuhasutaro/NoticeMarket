import os
import sys
import locale

class ResourceManager:
    @staticmethod
    def resource_path(rel_path):
        locale.setlocale(locale.LC_CTYPE, 'Japanese_Japan.932')
        if hasattr(sys, '_MEIPASS'):
            base = sys._MEIPASS
        else:
            base = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base, rel_path)
