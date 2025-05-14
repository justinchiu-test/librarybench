import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/live":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"alive")
        elif self.path == "/ready":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ready")
        else:
            self.send_response(404)
            self.end_headers()

    # suppress default logging
    def log_message(self, format, *args):
        return

def start_health_check(host="127.0.0.1", port=8000):
    """
    Starts a simple HTTPServer in a background thread serving /live and /ready.
    Returns the HTTPServer instance (runner).
    """
    server = HTTPServer((host, port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # attach the thread so we can optionally join or inspect
    server._thread = thread
    return server

def stop_health_check(runner):
    """
    Stops the HTTPServer runner.
    """
    runner.shutdown()
    runner.server_close()
    # if thread is non-daemon, you could join; but ours is daemon so it'll exit on process end
    if hasattr(runner, "_thread"):
        runner._thread.join(timeout=1)
