class Hooks:
    def __init__(self):
        self.pre = []
        self.post = []

    def register_pre(self, fn):
        self.pre.append(fn)

    def register_post(self, fn):
        self.post.append(fn)

    def run_pre(self, data):
        for fn in self.pre:
            try:
                fn(data)
            except Exception:
                pass

    def run_post(self, data):
        for fn in self.post:
            try:
                fn(data)
            except Exception:
                pass
