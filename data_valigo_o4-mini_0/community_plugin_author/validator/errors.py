class ErrorLocalizer:
    def __init__(self, default_lang='en'):
        self.default = default_lang
        self._backends = {}

    def register(self, lang: str, fn):
        self._backends[lang] = fn

    def translate(self, msg: str, lang: str = None) -> str:
        lang = lang or self.default
        fn = self._backends.get(lang)
        if fn:
            try:
                return fn(msg)
            except Exception:
                return msg
        return msg
