"""
Internationalization for Operations Engineer CLI.
Parses simple .po files.
"""
import os

def load_translations(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    result = {}
    key = None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('msgid '):
                key = line.split('msgid ',1)[1].strip().strip('"')
            elif line.startswith('msgstr '):
                val = line.split('msgstr ',1)[1].strip().strip('"')
                if key is not None:
                    result[key] = val
                    key = None
    return result