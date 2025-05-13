class MemoryUsageControl:
    def __init__(self, capacity):
        self.capacity = capacity
        self.current = 0
        self.spilled = False

    def add(self, item):
        if self.current + 1 > self.capacity:
            self.spilled = True
            return False
        self.current += 1
        return True
