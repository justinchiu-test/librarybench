class BuiltInMap:
    def __init__(self, map_fn):
        self.map_fn = map_fn

    def map(self, items):
        return [self.map_fn(i) for i in items]
