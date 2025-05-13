class Windowing:
    def __init__(self, window_size, step):
        self.window_size = window_size
        self.step = step

    def windows(self, items):
        result = []
        for i in range(0, len(items) - self.window_size + 1, self.step):
            result.append(items[i:i + self.window_size])
        return result
