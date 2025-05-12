# Defer import of prometheus_client and provide a fallback
try:
    from prometheus_client import start_http_server
except ImportError:
    # Provide a placeholder so tests can monkeypatch this name
    def start_http_server(port=8000):
        raise RuntimeError("prometheus_client not installed")

def start_prometheus_exporter(port=8000):
    start_http_server(port)
