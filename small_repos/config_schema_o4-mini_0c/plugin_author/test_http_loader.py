import http.server
import threading
import socket
import json
import pytest
import config_framework.core as core
from config_framework.core import load_config

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        response = {"hello": "world"}
        data = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, format, *args):
        pass

@pytest.fixture(scope="module")
def http_server():
    server = http.server.HTTPServer(('localhost', 0), SimpleHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield f"http://localhost:{port}/"
    server.shutdown()
    thread.join()

def test_http_loader_success(http_server):
    url = http_server
    data = load_config(url)
    assert isinstance(data, dict)
    assert data["hello"] == "world"

def test_http_loader_nonjson(tmp_path, monkeypatch):
    # serve plain text
    class TextHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            data = b"plain text"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, format, *args):
            pass
    server = http.server.HTTPServer(('localhost', 0), TextHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    url = f"http://localhost:{port}/"
    try:
        res = load_config(url)
        assert res == "plain text"
    finally:
        server.shutdown()
        thread.join()
