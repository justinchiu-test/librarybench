class Stage:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def process(self, item):
        return self.func(item)
