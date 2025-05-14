from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class MetricsExporter:
    def __init__(self, metrics, host='localhost', port=8000):
        self.metrics = metrics
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def _make_handler(self):
        metrics = self.metrics
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain;version=0.0.4')
                    self.end_headers()
                    lines = []
                    for stage, counts in metrics.counters.items():
                        for status, count in counts.items():
                            lines.append(f'pipeline_{stage}_{status} {count}')
                    self.wfile.write('\n'.join(lines).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                return
        return Handler

    def start(self):
        handler = self._make_handler()
        self.server = HTTPServer((self.host, self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.thread.join()
