_locale = 'en'
_translations = {}

def set_locale(locale):
    global _locale
    _locale = locale

def add_translation(locale, key, value):
    _translations[(locale, key)] = value

def translate_text(text):
    return _translations.get((_locale, text), text)
