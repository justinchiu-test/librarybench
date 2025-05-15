import os

def load_translations(locale_dir: str) -> dict:
    translations = {}
    if not os.path.isdir(locale_dir):
        return translations
    for fname in os.listdir(locale_dir):
        if fname.endswith(".po"):
            path = os.path.join(locale_dir, fname)
            with open(path, encoding="utf-8") as f:
                translations[fname] = f.read()
    return translations
