class I18n:
    """
    Simple in-memory translation registry.
    """
    def __init__(self):
        self.translations = {}

    def load(self, locale, mapping):
        """
        Load a dict of key->translated string for a locale.
        """
        self.translations[locale] = mapping

    def translate(self, key, locale):
        """
        Translate a key for given locale; fallback to key if missing.
        """
        return self.translations.get(locale, {}).get(key, key)
