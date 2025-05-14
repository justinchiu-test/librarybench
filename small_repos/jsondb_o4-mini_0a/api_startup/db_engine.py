import os
import json
import threading
import time
import tempfile

class DBEngine:
    def __init__(self, path='data/events.json', encryption_key=None):
        self.path = path
        self.dir = os.path.dirname(self.path)
        if self.dir and not os.path.exists(self.dir):
            os.makedirs(self.dir)
        # simple XOR encryption key
        if encryption_key is None:
            self.key = os.urandom(16)
        else:
            self.key = encryption_key
        self.events = {}  # id -> event dict including metadata
        self.next_id = 1
        self.ttl = None
        self.sweeper_thread = None
        self.indexes = {}  # tuple(fields) -> {tuple(values): set(ids)}
        self.plugins = []
        # load existing
        if os.path.exists(self.path):
            self._load()
        self._build_indexes()

    def _encrypt(self, data_bytes):
        out = bytearray(data_bytes)
        for i in range(len(out)):
            out[i] ^= self.key[i % len(self.key)]
        return bytes(out)

    def _decrypt(self, data_bytes):
        # symmetric
        return self._encrypt(data_bytes)

    def _persist(self):
        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.dir or '.', prefix='events.json.', text=False)
        try:
            with os.fdopen(tmp_fd, 'wb') as f:
                data = json.dumps(self.events).encode('utf-8')
                f.write(self._encrypt(data))
            os.replace(tmp_path, self.path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    def _load(self):
        with open(self.path, 'rb') as f:
            data = f.read()
            plain = self._decrypt(data)
            obj = json.loads(plain.decode('utf-8'))
            self.events = {int(k): v for k, v in obj.items()}
            if self.events:
                self.next_id = max(self.events.keys()) + 1

    def _build_indexes(self):
        for idx_fields in self.indexes:
            self.indexes[idx_fields] = {}
        for eid, evt in self.events.items():
            self._update_indexes_on_insert(eid, evt)

    def setTTL(self, seconds):
        self.ttl = seconds
        if self.sweeper_thread is None:
            t = threading.Thread(target=self._sweeper, daemon=True)
            self.sweeper_thread = t
            t.start()

    def _sweeper(self):
        while True:
            now = time.time()
            to_delete = []
            for eid, evt in list(self.events.items()):
                if self.ttl is not None and now - evt.get('_insert_time', evt.get('timestamp', now)) > self.ttl:
                    to_delete.append(eid)
            for eid in to_delete:
                self.delete(id=eid, soft=False)
            time.sleep(1)

    def createIndex(self, fields):
        if isinstance(fields, str):
            fields = [fields]
        key = tuple(fields)
        if key in self.indexes:
            return
        self.indexes[key] = {}
        # build index
        for eid, evt in self.events.items():
            vals = tuple(evt.get(f) for f in fields)
            self.indexes[key].setdefault(vals, set()).add(eid)

    def _update_indexes_on_insert(self, eid, evt):
        for fields, idx in self.indexes.items():
            vals = tuple(evt.get(f) for f in fields)
            idx.setdefault(vals, set()).add(eid)

    def _update_indexes_on_delete(self, eid, evt):
        for fields, idx in self.indexes.items():
            vals = tuple(evt.get(f) for f in fields)
            if vals in idx and eid in idx[vals]:
                idx[vals].remove(eid)
                if not idx[vals]:
                    del idx[vals]

    def registerPlugin(self, plugin):
        self.plugins.append(plugin)
        plugin.register(self)

    def enforce_schema(self, evt):
        if not isinstance(evt, dict):
            raise ValueError("Event must be a dict")
        if 'timestamp' not in evt or 'userID' not in evt or 'eventType' not in evt:
            raise ValueError("Missing required field")
        if not isinstance(evt['timestamp'], (int, float)):
            raise ValueError("timestamp must be number")
        if not isinstance(evt['userID'], str):
            raise ValueError("userID must be string")
        if not isinstance(evt['eventType'], str):
            raise ValueError("eventType must be string")

    def upsert(self, evt):
        self.enforce_schema(evt)
        eid = self.next_id
        self.next_id += 1
        # metadata
        evt_copy = dict(evt)
        evt_copy['_insert_time'] = time.time()
        evt_copy['_deleted'] = False
        self.events[eid] = evt_copy
        self._update_indexes_on_insert(eid, evt_copy)
        self._persist()
        for plugin in self.plugins:
            if hasattr(plugin, 'on_upsert'):
                plugin.on_upsert(eid, evt_copy)
        return eid

    def batchUpsert(self, evts):
        saved_events = dict(self.events)
        saved_next = self.next_id
        saved_indexes = {k: {vk: set(vs) for vk, vs in idx.items()} for k, idx in self.indexes.items()}
        try:
            ids = []
            for evt in evts:
                eid = self.upsert(evt)
                ids.append(eid)
            return ids
        except Exception as e:
            # rollback
            self.events = saved_events
            self.next_id = saved_next
            self.indexes = saved_indexes
            self._persist()
            raise

    def query(self, filters=None):
        res = []
        # special-case lookup by id
        if filters and 'id' in filters and len(filters) == 1:
            eid = filters['id']
            evt = self.events.get(eid)
            if evt and not evt.get('_deleted', False):
                res.append({'id': eid, **{k: v for k, v in evt.items() if not k.startswith('_')}})
            return res

        if not filters:
            for eid, evt in self.events.items():
                if not evt.get('_deleted', False):
                    res.append({'id': eid, **{k: v for k, v in evt.items() if not k.startswith('_')}})
            return res
        # if indexed
        for fields, idx in self.indexes.items():
            if set(filters.keys()) == set(fields):
                key = tuple(filters[f] for f in fields)
                ids = idx.get(key, set())
                for eid in ids:
                    evt = self.events[eid]
                    if not evt.get('_deleted', False):
                        res.append({'id': eid, **{k: v for k, v in evt.items() if not k.startswith('_')}})
                return res
        # fallback scan
        for eid, evt in self.events.items():
            if evt.get('_deleted', False):
                continue
            match = True
            for k, v in filters.items():
                if evt.get(k) != v:
                    match = False
                    break
            if match:
                res.append({'id': eid, **{k: v for k, v in evt.items() if not k.startswith('_')}})
        return res

    def delete(self, id=None, query=None, soft=False):
        to_delete = []
        if id is not None:
            if id in self.events:
                to_delete = [id]
        elif query is not None:
            found = self.query(query)
            to_delete = [evt['id'] for evt in found]
        for eid in to_delete:
            evt = self.events.get(eid)
            if evt is None:
                continue
            if soft:
                evt['_deleted'] = True
                self.events[eid] = evt
            else:
                self._update_indexes_on_delete(eid, evt)
                del self.events[eid]
        self._persist()

    def softDelete(self, id):
        self.delete(id=id, soft=True)

    def undelete(self, id):
        evt = self.events.get(id)
        if evt and evt.get('_deleted', False):
            evt['_deleted'] = False
            self.events[id] = evt
            self._persist()

    def startRestServer(self, host='127.0.0.1', port=5000):
        # Try Flask; if unavailable, fallback to stdlib HTTP server
        try:
            from flask import Flask, request, jsonify, abort
        except ModuleNotFoundError:
            # Fallback HTTP server
            from http.server import HTTPServer, BaseHTTPRequestHandler
            from urllib.parse import urlparse, parse_qs
            import json as _json
            engine = self

            class Handler(BaseHTTPRequestHandler):
                def do_POST(self):
                    parsed = urlparse(self.path)
                    path = parsed.path
                    qs = parse_qs(parsed.query)
                    length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(length) if length else b''
                    data = None
                    if body:
                        try:
                            data = _json.loads(body.decode('utf-8'))
                        except:
                            data = None
                    try:
                        if path == '/events':
                            eid = engine.upsert(data)
                            resp = {'id': eid}
                            self.send_response(201)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(_json.dumps(resp).encode('utf-8'))
                        elif path == '/events/batch':
                            ids = engine.batchUpsert(data)
                            resp = {'ids': ids}
                            self.send_response(201)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(_json.dumps(resp).encode('utf-8'))
                        elif path.startswith('/events/') and path.endswith('/undelete'):
                            parts = path.rstrip('/').split('/')
                            eid = int(parts[2])
                            engine.undelete(eid)
                            self.send_response(204)
                            self.end_headers()
                        elif path == '/admin/ttl':
                            seconds = data.get('ttl')
                            engine.setTTL(seconds)
                            self.send_response(204)
                            self.end_headers()
                        elif path == '/admin/index':
                            fields = data.get('fields')
                            engine.createIndex(fields)
                            self.send_response(204)
                            self.end_headers()
                        else:
                            self.send_response(404)
                            self.end_headers()
                    except Exception as e:
                        if path in ['/events', '/events/batch']:
                            self.send_response(400)
                            self.send_header('Content-Type', 'text/plain')
                            self.end_headers()
                            self.wfile.write(str(e).encode('utf-8'))
                        else:
                            self.send_response(500)
                            self.end_headers()

                def do_GET(self):
                    parsed = urlparse(self.path)
                    path = parsed.path
                    qs = parse_qs(parsed.query)
                    if path == '/events':
                        filters = {k: v[0] for k, v in qs.items()} if qs else None
                        res = engine.query(filters)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(_json.dumps(res).encode('utf-8'))
                    elif path.startswith('/events/'):
                        parts = path.rstrip('/').split('/')
                        if len(parts) == 3:
                            try:
                                eid = int(parts[2])
                                result = engine.query({'id': eid})
                                if not result:
                                    self.send_response(404)
                                    self.end_headers()
                                else:
                                    self.send_response(200)
                                    self.send_header('Content-Type', 'application/json')
                                    self.end_headers()
                                    self.wfile.write(_json.dumps(result[0]).encode('utf-8'))
                            except:
                                self.send_response(404)
                                self.end_headers()
                        else:
                            self.send_response(404)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def do_DELETE(self):
                    parsed = urlparse(self.path)
                    path = parsed.path
                    qs = parse_qs(parsed.query)
                    if path.startswith('/events/'):
                        parts = path.rstrip('/').split('/')
                        if len(parts) == 3:
                            try:
                                eid = int(parts[2])
                                soft = qs.get('soft', ['false'])[0].lower() == 'true'
                                engine.delete(id=eid, soft=soft)
                                self.send_response(204)
                                self.end_headers()
                            except:
                                self.send_response(404)
                                self.end_headers()
                        else:
                            self.send_response(404)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def log_message(self, format, *args):
                    # suppress logging
                    return

            server = HTTPServer((host, port), Handler)
            server.serve_forever()
            return

        # Flask-based REST server
        app = Flask(__name__)
        engine = self

        @app.route('/events', methods=['POST'])
        def create_event():
            evt = request.get_json()
            try:
                eid = engine.upsert(evt)
                return jsonify({'id': eid}), 201
            except Exception as e:
                abort(400, str(e))

        @app.route('/events/batch', methods=['POST'])
        def batch_events():
            evts = request.get_json()
            try:
                ids = engine.batchUpsert(evts)
                return jsonify({'ids': ids}), 201
            except Exception as e:
                abort(400, str(e))

        @app.route('/events', methods=['GET'])
        def list_events():
            filters = request.args.to_dict()
            res = engine.query(filters if filters else None)
            return jsonify(res)

        @app.route('/events/<int:eid>', methods=['GET'])
        def get_event(eid):
            res = engine.query({'id': eid})
            if not res:
                abort(404)
            return jsonify(res[0])

        @app.route('/events/<int:eid>', methods=['DELETE'])
        def delete_event(eid):
            soft = request.args.get('soft', 'false').lower() == 'true'
            engine.delete(id=eid, soft=soft)
            return '', 204

        @app.route('/events/<int:eid>/undelete', methods=['POST'])
        def undelete_event(eid):
            engine.undelete(eid)
            return '', 204

        @app.route('/admin/ttl', methods=['POST'])
        def set_ttl():
            data = request.get_json()
            seconds = data.get('ttl')
            engine.setTTL(seconds)
            return '', 204

        @app.route('/admin/index', methods=['POST'])
        def add_index():
            data = request.get_json()
            fields = data.get('fields')
            engine.createIndex(fields)
            return '', 204

        app.run(host=host, port=port)
