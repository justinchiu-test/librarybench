class AnomalyDetector:
    def __init__(self):
        self.callbacks = []
        self.anomalies = []

    def register(self, func):
        self.callbacks.append(func)

    def run(self, record):
        for cb in self.callbacks:
            try:
                if cb(record):
                    self.anomalies.append(record)
            except Exception:
                pass
