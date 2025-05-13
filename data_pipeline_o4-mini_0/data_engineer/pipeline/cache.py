class CachingStage:
    def __init__(self, key_func):
        self.cache = {}
        self.key_func = key_func

    def process(self, records):
        result = []
        for r in records:
            key = self.key_func(r)
            if key in self.cache:
                result.append(self.cache[key])
            else:
                self.cache[key] = r
                result.append(r)
        return result
