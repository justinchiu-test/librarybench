class ContextPropagation:
    def __init__(self, context: dict = None):
        self.context = context or {}

    def get_context(self):
        return self.context
