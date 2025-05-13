"""
Internationalization for Translator CLI adapter.
"""
class I18n:
    def __init__(self):
        self._data = {}

    def load(self, locale, mapping):
        self._data[locale] = mapping or {}

    def translate(self, key, locale):
        return self._data.get(locale, {}).get(key, key)