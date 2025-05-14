import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

def make_app(db):
    class RequestHandler(BaseHTTPRequestHandler):
        def _send(self, code, data):
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if data is not None:
                self.wfile.write(json.dumps(data).encode('utf-8'))

        def do_GET(self):
            parsed = urlparse(self.path)
            parts = parsed.path.strip('/').split('/')
            if parts[0] == 'entries':
                if len(parts) == 1:
                    entries = list(db.entries.values())
                    self._send(200, entries)
                elif len(parts) == 2:
                    eid = parts[1]
                    entry = db.entries.get(eid)
                    if entry:
                        self._send(200, entry)
                    else:
                        self._send(404, {'error': 'Not found'})
                else:
                    self._send(404, {'error': 'Not found'})
            else:
                self._send(404, {'error': 'Not found'})

        def do_POST(self):
            parsed = urlparse(self.path)
            parts = parsed.path.strip('/').split('/')
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length > 0 else b''
            try:
                data = json.loads(body.decode('utf-8')) if body else None
            except:
                data = None
            if parts[0] == 'entries':
                if len(parts) == 1:
                    try:
                        db.upsert(data)
                        self._send(200, {'status': 'ok'})
                    except Exception as e:
                        self._send(400, {'error': str(e)})
                elif len(parts) == 2 and parts[1] == 'batch':
                    try:
                        db.batchUpsert(data or [])
                        self._send(200, {'status': 'ok'})
                    except Exception as e:
                        self._send(400, {'error': str(e)})
                else:
                    self._send(404, {'error': 'Not found'})
            else:
                self._send(404, {'error': 'Not found'})

        def do_DELETE(self):
            parsed = urlparse(self.path)
            parts = parsed.path.strip('/').split('/')
            if parts[0] == 'entries' and len(parts) == 2:
                eid = parts[1]
                db.delete_by_id(eid)
                self._send(200, {'status': 'deleted'})
            else:
                self._send(404, {'error': 'Not found'})

        def log_message(self, format, *args):
            return

    server = HTTPServer(('localhost', port), RequestHandler)
    return server
