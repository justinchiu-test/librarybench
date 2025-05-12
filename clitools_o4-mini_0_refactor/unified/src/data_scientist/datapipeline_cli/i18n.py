"""
Internationalization for data scientists.
"""
_TRANSLATIONS = {
    'en': {'greet': 'Hello', 'farewell': 'Goodbye'},
    'es': {'greet': 'Hola', 'farewell': 'Adiós'},
}

def load_translations(lang):
    return _TRANSLATIONS.get(lang, {})