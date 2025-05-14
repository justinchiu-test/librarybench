from time import time

class Metrics:
    def __init__(self):
        self.counters = {}

    def increment(self, name):
        self.counters[name] = self.counters.get(name, 0) + 1

    def expose(self):
        lines = []
        for k, v in self.counters.items():
            lines.append(f"{k} {v}")
        return "\n".join(lines), 200, {'Content-Type': 'text/plain; version=0.0.4'}
