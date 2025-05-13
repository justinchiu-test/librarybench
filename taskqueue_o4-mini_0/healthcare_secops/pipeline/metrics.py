class MetricsIntegration:
    def __init__(self):
        self.metrics = []

    def send(self, name: str, value):
        self.metrics.append({'name': name, 'value': value})

    def get_metrics(self):
        return list(self.metrics)
