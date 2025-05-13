class BuiltInFilter:
    def __init__(self, predicate):
        self.predicate = predicate

    def filter(self, items):
        return [i for i in items if self.predicate(i)]
