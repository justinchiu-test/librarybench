class TransformationHook:
    def __init__(self):
        self.funcs = []

    def register(self, func):
        self.funcs.append(func)

    def apply(self, record):
        for func in self.funcs:
            try:
                record = func(record) or record
            except Exception:
                pass
        return record
