"""
Internationalization support for translator.
"""
class I18n:
    def __init__(self):
        self._translations = {}

    def load(self, locale, mappings):
        # mappings: dict of key->translation
        self._translations[locale] = mappings.copy()

    def translate(self, key, locale):
        return self._translations.get(locale, {}).get(key, key)