class ContextPropagation:
    def __init__(self, **kwargs):
        # store the original context
        self.context = dict(kwargs)

    def get_context(self):
        # return a shallow copy so external mutations don't affect the original
        return self.context.copy()
