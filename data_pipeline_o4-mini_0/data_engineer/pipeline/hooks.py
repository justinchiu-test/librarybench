class SourceSinkHooks:
    def __init__(self):
        self.pre_hooks = []
        self.post_hooks = []

    def register_pre(self, fn):
        self.pre_hooks.append(fn)

    def register_post(self, fn):
        self.post_hooks.append(fn)

    def run_pre(self, record):
        for fn in self.pre_hooks:
            record = fn(record)
        return record

    def run_post(self, record):
        for fn in self.post_hooks:
            record = fn(record)
        return record
