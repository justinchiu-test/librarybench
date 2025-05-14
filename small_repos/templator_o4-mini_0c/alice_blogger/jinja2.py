# Stub jinja2 module for testing purposes

class TemplateSyntaxError(Exception):
    def __init__(self, message, lineno=None, name=None):
        super().__init__(message)
        self.lineno = lineno
        self.name = name

class TemplateError(Exception):
    pass
