from . import config

class PrometheusExporter:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_metrics(self):
        # Return a snapshot of all counters
        return {name: counter.get() for name, counter in config.counters.items()}

def start_prometheus_exporter(host='0.0.0.0', port=8000):
    # Stub: return exporter instance
    return PrometheusExporter(host, port)
