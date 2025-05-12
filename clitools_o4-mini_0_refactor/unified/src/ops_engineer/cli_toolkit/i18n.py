"""
Internationalization for ops engineers.
"""
"""
Load translations from a .po file for ops engineers.
"""
import os

def load_translations(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    translations = {}
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('msgid'):
            # extract msgid
            key = line.split('msgid', 1)[1].strip().strip('"')
            i += 1
            if i < len(lines) and lines[i].startswith('msgstr'):
                val = lines[i].split('msgstr', 1)[1].strip().strip('"')
                translations[key] = val
        i += 1
    return translations