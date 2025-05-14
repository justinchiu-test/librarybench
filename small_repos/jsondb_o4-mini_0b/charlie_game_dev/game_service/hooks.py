class Hooks:
    def __init__(self):
        self.pre_write = []
        self.post_write = []

    def register_pre(self, fn):
        self.pre_write.append(fn)

    def register_post(self, fn):
        self.post_write.append(fn)

hooks = Hooks()
