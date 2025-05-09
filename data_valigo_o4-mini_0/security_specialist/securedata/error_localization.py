class ErrorLocalization:
    def __init__(self, translations=None):
        self.translations = translations or {}

    def translate(self, message_key: str, lang: str = 'en') -> str:
        return self.translations.get(lang, {}).get(message_key, message_key)

    def register_translation(self, lang: str, translations: dict):
        self.translations.setdefault(lang, {}).update(translations)
