import os
import json
import threading
import time
import shutil
from datetime import datetime, timedelta
# import validate and ValidationError from our local jsonschema module
from jsonschema import validate, ValidationError

# Attempt to import cryptography; if unavailable, run in plaintext mode
try:
    from cryptography.hazmat.primitives import padding as sympadding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    HAVE_CRYPTO = True
except ImportError:
    HAVE_CRYPTO = False

class JSONDB:
    def __init__(self, path='db.json'):
        self.path = path
        self.lock = threading.Lock()
        self.data = {'players': {}, 'matches': {}}
        self.ttls = {}       # collection -> seconds
        self.indices = {}    # collection -> field -> {value -> set(ids)}
        self.schemas = {}    # collection -> schema dict
        self.plugins = []
        self.key = None
        # only set backend if crypto is available
        self.backend = default_backend() if HAVE_CRYPTO else None
        # load existing
        if os.path.exists(self.path):
            try:
                self._load()
            except Exception:
                # corrupted or unreadable, start fresh
                self.data = {'players': {}, 'matches': {}}

    def setTTL(self, collection, hours):
        self.ttls[collection] = hours * 3600

    def createIndex(self, collection, field):
        idx = {}
        for _id, doc in self.data.get(collection, {}).items():
            val = doc.get(field)
            if val is not None:
                idx.setdefault(val, set()).add(_id)
        self.indices.setdefault(collection, {})[field] = idx

    def encryptAtRest(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")
        self.key = key

    def enforceSchema(self, collection, schema: dict):
        self.schemas[collection] = schema

    def registerPlugin(self, plugin):
        self.plugins.append(plugin)

    def batchUpsert(self, collection, items):
        with self.lock:
            for item in items:
                self._upsert(collection, item)
            self._apply_ttl(collection)
            self._persist()

    def persistAtomically(self):
        with self.lock:
            self._apply_ttl_all()
            self._persist()

    def delete(self, collection, _id=None, filter=None):
        with self.lock:
            coll = self.data.get(collection, {})
            targets = []
            if _id is not None:
                if _id in coll:
                    targets = [_id]
            elif filter is not None:
                for k, doc in coll.items():
                    match = True
                    for fk, fv in filter.items():
                        if doc.get(fk) != fv:
                            match = False
                            break
                    if match:
                        targets.append(k)
            for tid in targets:
                coll.pop(tid, None)
                # remove from indices
                if collection in self.indices:
                    for field, idx in self.indices[collection].items():
                        for v, s in idx.items():
                            s.discard(tid)
            self._persist()

    def softDelete(self, collection, _id=None, filter=None):
        with self.lock:
            coll = self.data.get(collection, {})
            for k, doc in coll.items():
                do_delete = False
                if _id is not None and k == _id:
                    do_delete = True
                elif filter is not None:
                    match = True
                    for fk, fv in filter.items():
                        if doc.get(fk) != fv:
                            match = False
                            break
                    if match:
                        do_delete = True
                if do_delete:
                    doc['deleted'] = True
            self._persist()

    def startRestServer(self, host='127.0.0.1', port=5000):
        """
        A minimal REST server without external dependencies.
        Supports:
          GET  /<collection>
          POST /<collection>         JSON body
          DELETE /<collection>/<id>?soft=1|0
        """
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse

        db = self

        class Handler(BaseHTTPRequestHandler):
            def _send_json(self, data, status=200):
                resp = json.dumps(data).encode('utf-8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                parts = parsed.path.strip('/').split('/')
                if len(parts) != 1:
                    self._send_json({'error': 'Invalid endpoint'}, 404)
                    return
                collection = parts[0]
                if collection not in db.data:
                    self._send_json({'error': 'Unknown collection'}, 404)
                    return
                self._send_json(db.data[collection], 200)

            def do_POST(self):
                parsed = urllib.parse.urlparse(self.path)
                parts = parsed.path.strip('/').split('/')
                if len(parts) != 1:
                    self._send_json({'error': 'Invalid endpoint'}, 404)
                    return
                collection = parts[0]
                if collection not in db.data:
                    self._send_json({'error': 'Unknown collection'}, 404)
                    return
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    doc = json.loads(body.decode('utf-8'))
                except Exception:
                    self._send_json({'error': 'Invalid JSON'}, 400)
                    return
                try:
                    db._upsert(collection, doc)
                    db.persistAtomically()
                except ValidationError as e:
                    self._send_json({'error': str(e)}, 400)
                    return
                self._send_json({'status': 'ok'}, 201)

            def do_DELETE(self):
                parsed = urllib.parse.urlparse(self.path)
                parts = parsed.path.strip('/').split('/')
                if len(parts) != 2:
                    self._send_json({'error': 'Invalid endpoint'}, 404)
                    return
                collection, doc_id = parts
                if collection not in db.data:
                    self._send_json({'error': 'Unknown collection'}, 404)
                    return
                qs = urllib.parse.parse_qs(parsed.query)
                soft = qs.get('soft', ['0'])[0] == '1'
                if soft:
                    db.softDelete(collection, _id=doc_id)
                else:
                    db.delete(collection, _id=doc_id)
                self._send_json({'status': 'deleted'}, 200)

            def log_message(self, format, *args):
                # suppress default logging
                return

        def serve():
            httpd = HTTPServer((host, port), Handler)
            httpd.serve_forever()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()

    # Internal methods
    def _upsert(self, collection, doc):
        if 'id' not in doc:
            raise ValueError("Document must have 'id'")
        schema = self.schemas.get(collection)
        if schema:
            validate(instance=doc, schema=schema)
        _id = doc['id']
        doc_copy = dict(doc)
        if collection == 'matches':
            doc_copy['timestamp'] = time.time()
        self.data.setdefault(collection, {})[_id] = doc_copy
        # update indices
        if collection in self.indices:
            for field, idx in self.indices[collection].items():
                val = doc_copy.get(field)
                if val is not None:
                    idx.setdefault(val, set()).add(_id)
        for plugin in self.plugins:
            if hasattr(plugin, 'after_upsert'):
                plugin.after_upsert(collection, doc_copy)

    def _apply_ttl(self, collection):
        if collection in self.ttls:
            now = time.time()
            ttl = self.ttls[collection]
            coll = self.data.get(collection, {})
            to_delete = [k for k, d in coll.items()
                         if 'timestamp' in d and (now - d['timestamp'] > ttl)]
            for k in to_delete:
                coll.pop(k, None)

    def _apply_ttl_all(self):
        for collection in list(self.ttls.keys()):
            self._apply_ttl(collection)

    def _persist(self):
        """
        Atomically write self.data to self.path.
        If encryption key is set and cryptography is available, encrypt the JSON blob.
        """
        json_str = json.dumps(self.data)
        if self.key and HAVE_CRYPTO:
            raw = json_str.encode('utf-8')
            iv = os.urandom(16)
            padder = sympadding.PKCS7(128).padder()
            padded = padder.update(raw) + padder.finalize()
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ct = encryptor.update(padded) + encryptor.finalize()
            to_write = iv + ct
            mode = 'wb'
        else:
            to_write = json_str
            mode = 'w'
        tmp = self.path + '.tmp'
        with open(tmp, mode) as f:
            f.write(to_write)
        shutil.move(tmp, self.path)

    def _load(self):
        """
        Load the database from disk, handling decryption if needed.
        """
        if self.key and HAVE_CRYPTO:
            with open(self.path, 'rb') as f:
                data = f.read()
            iv = data[:16]
            ct = data[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded = decryptor.update(ct) + decryptor.finalize()
            unpadder = sympadding.PKCS7(128).unpadder()
            raw = unpadder.update(padded) + unpadder.finalize()
            self.data = json.loads(raw.decode('utf-8'))
        else:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
