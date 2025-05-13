"""
Internationalization loader for backend_dev microcli.
Loads .po files from a locale directory.
"""
import os

def load_translations(path):
    """
    Load .po translation files from the given directory.
    Returns dict: filename -> content.
    """
    translations = {}
    if not os.path.isdir(path):
        return translations
    for fn in os.listdir(path):
        if fn.endswith('.po'):
            full = os.path.join(path, fn)
            try:
                with open(full, 'r', encoding='utf-8') as f:
                    translations[fn] = f.read()
            except IOError:
                continue
    return translations