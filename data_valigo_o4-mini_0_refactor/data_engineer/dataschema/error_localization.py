class ErrorLocalization:
    def __init__(self):
        # translations: {code: {lang: template}}
        self._translations = {}

    def register(self, code: str, lang: str, template: str):
        self._translations.setdefault(code, {})[lang] = template

    def translate(self, code: str, lang: str, **kwargs) -> str:
        templates = self._translations.get(code, {})
        template = templates.get(lang) or templates.get('en')
        if not template:
            return code
        return template.format(**kwargs)
