class BuiltInBatch:
    def __init__(self, window_size):
        self.window_size = window_size

    def batch(self, items):
        batches = []
        for i in range(0, len(items), self.window_size):
            batches.append(items[i:i + self.window_size])
        return batches
