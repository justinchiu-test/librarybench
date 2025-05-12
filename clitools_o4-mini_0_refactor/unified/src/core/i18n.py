"""
Internationalization support: load translations from .po files.
"""
import os

def load_translations(path):
    trans = {}
    if not os.path.isdir(path):
        return trans
    for fname in os.listdir(path):
        if fname.endswith('.po'):
            try:
                with open(os.path.join(path, fname), 'r', encoding='utf-8') as f:
                    content = f.read()
                trans[fname] = content
            except Exception:
                continue
    return trans