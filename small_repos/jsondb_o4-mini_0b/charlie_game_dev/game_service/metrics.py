class Metrics:
    def __init__(self):
        self.counters = {'save_latency': 0, 'load_latency': 0, 'index_hit_rate': 0}

    def inc(self, name, value=1):
        self.counters[name] = self.counters.get(name, 0) + value

    def get(self, name):
        return self.counters.get(name, 0)

metrics = Metrics()
