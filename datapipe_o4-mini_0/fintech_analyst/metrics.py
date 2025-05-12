metrics_store = {}

def export_prometheus_metrics(name, value):
    metrics_store[name] = value

def get_metric(name):
    return metrics_store.get(name)
