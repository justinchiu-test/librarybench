import copy

class ContextPropagation:
    def __init__(self, **tags):
        self.tags = tags.copy()

    def update(self, **tags):
        self.tags.update(tags)

    def get(self, key, default=None):
        return self.tags.get(key, default)

    def clone(self):
        new = ContextPropagation(**self.tags)
        return new

class retry_scope:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
