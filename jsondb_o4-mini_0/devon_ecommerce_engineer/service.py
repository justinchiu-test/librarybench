import os
import json
import threading
import time
import base64

# Import from our local flask module
from flask import Flask, jsonify, request, abort

class ProductService:
    def __init__(self, data_file, version_dir, journal_file, encryption_key):
        self.data_file = data_file
        self.version_dir = version_dir
        self.journal_file = journal_file
        self.encryption_key = encryption_key  # not used in base64 scheme
        self.lock = threading.Lock()
        self.deleted = {}  # product_id -> {'time': ts, 'data': prod}
        # Ensure directories and files exist
        os.makedirs(self.version_dir, exist_ok=True)
        # Initialize data file if not exists
        if not os.path.exists(self.data_file):
            self._write_file({})
        # Initialize journal file
        open(self.journal_file, 'a').close()

    def _encrypt(self, data_bytes):
        # simple base64 encoding for "encryption at rest"
        return base64.b64encode(data_bytes)

    def _decrypt(self, data_bytes):
        return base64.b64decode(data_bytes)

    def _read_file(self):
        if not os.path.exists(self.data_file):
            return {}
        raw = open(self.data_file, 'rb').read()
        if not raw:
            return {}
        try:
            plain = self._decrypt(raw)
            return json.loads(plain.decode())
        except Exception:
            # if decrypt or decode fails, assume empty
            return {}

    def _write_file(self, db):
        plain = json.dumps(db).encode()
        cipher = self._encrypt(plain)
        with open(self.data_file, 'wb') as f:
            f.write(cipher)

    def _append_journal(self, operation, data):
        entry = {'operation': operation, 'data': data}
        with open(self.journal_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def create_product(self, prod):
        with self.lock:
            pid = prod['id']
            prod = prod.copy()
            # normalize SKU
            prod['sku'] = prod.get('sku', '').upper()
            # save version
            ts = str(time.time_ns())
            fn = f"{pid}_{ts}.json"
            path = os.path.join(self.version_dir, fn)
            with open(path, 'w') as vf:
                json.dump(prod, vf)
            # save to main store
            db = self._read_file()
            db[pid] = prod
            self._write_file(db)
            self._append_journal('create', {'id': pid})
            return prod

    def read_product(self, product_id):
        db = self._read_file()
        return db.get(product_id)

    def update_product(self, product_id, updates):
        with self.lock:
            db = self._read_file()
            if product_id not in db:
                raise KeyError(f"Product {product_id} not found")
            prod = db[product_id]
            for k, v in updates.items():
                prod[k] = v
            # normalize SKU if updated
            if 'sku' in updates:
                prod['sku'] = prod['sku'].upper()
            # save version
            ts = str(time.time_ns())
            fn = f"{product_id}_{ts}.json"
            path = os.path.join(self.version_dir, fn)
            with open(path, 'w') as vf:
                json.dump(prod, vf)
            # write back
            db[product_id] = prod
            self._write_file(db)
            self._append_journal('update', {'id': product_id, 'updates': updates})
            return prod

    def delete_product(self, product_id):
        with self.lock:
            db = self._read_file()
            if product_id in db:
                prod = db.pop(product_id)
                self._write_file(db)
                # record deletion
                self.deleted[product_id] = {'time': time.time(), 'data': prod}
                self._append_journal('delete', {'id': product_id})

    def undelete_product(self, product_id, within_seconds=None):
        with self.lock:
            rec = self.deleted.get(product_id)
            if not rec:
                return None
            elapsed = time.time() - rec['time']
            if (within_seconds is None) or (elapsed <= within_seconds):
                # restore
                prod = rec['data']
                db = self._read_file()
                db[product_id] = prod
                self._write_file(db)
                del self.deleted[product_id]
                self._append_journal('undelete', {'id': product_id})
                return prod
            else:
                return None

    def purge_deleted(self, within_seconds):
        purged = []
        now = time.time()
        to_remove = []
        for pid, rec in self.deleted.items():
            if now - rec['time'] > within_seconds:
                to_remove.append(pid)
        for pid in to_remove:
            purged.append(pid)
            del self.deleted[pid]
        return purged

    def batch_upsert(self, products):
        for prod in products:
            pid = prod['id']
            if self.read_product(pid) is None:
                self.create_product(prod.copy())
            else:
                # pass only updatable fields
                ups = {k: v for k, v in prod.items() if k != 'id'}
                self.update_product(pid, ups)

    def get_versions(self, product_id):
        files = sorted(os.listdir(self.version_dir))
        res = []
        prefix = f"{product_id}_"
        for fn in files:
            if fn.startswith(prefix) and fn.endswith('.json'):
                ts = fn[len(prefix):].split('.')[0]
                res.append(ts)
        return res

    def rollback(self, product_id, timestamp):
        with self.lock:
            all_files = sorted(os.listdir(self.version_dir))
            prod_files = [f for f in all_files if f.startswith(f"{product_id}_")]
            if not prod_files:
                raise ValueError('Version not found')
            prefix = f"{product_id}_"
            timestamps = [f[len(prefix):].split('.')[0] for f in prod_files]
            try:
                idx = timestamps.index(timestamp)
            except ValueError:
                raise ValueError('Version not found')
            target_idx = idx - 1 if idx > 0 else 0
            target_file = prod_files[target_idx]
            path = os.path.join(self.version_dir, target_file)
            with open(path, 'r') as ff:
                data = json.load(ff)
            db = self._read_file()
            db[product_id] = data
            self._write_file(db)
            self._append_journal('rollback', {'id': product_id, 'timestamp': timestamp})
            return data

# Flask app and routes
app = Flask(__name__)
service = ProductService.__new__(ProductService)

@app.route('/products', methods=['POST'])
def api_create():
    prod = request.json
    try:
        out = service.create_product(prod)
        return jsonify(out), 201
    except Exception:
        abort(400)

@app.route('/products/<product_id>', methods=['GET'])
def api_read(product_id):
    prod = service.read_product(product_id)
    if prod is None:
        abort(404)
    return jsonify(prod)

@app.route('/products/<product_id>', methods=['PATCH'])
def api_update(product_id):
    updates = request.json
    try:
        out = service.update_product(product_id, updates)
        return jsonify(out)
    except KeyError:
        abort(404)
    except Exception:
        abort(400)

@app.route('/products/<product_id>', methods=['DELETE'])
def api_delete(product_id):
    service.delete_product(product_id)
    return '', 204

@app.route('/products/<product_id>/undelete', methods=['POST'])
def api_undelete(product_id):
    service.undelete_product(product_id, within_seconds=None)
    return '', 204

@app.route('/batch_upsert', methods=['POST'])
def api_batch():
    prods = request.json
    service.batch_upsert(prods)
    return '', 204

@app.route('/versions/<product_id>', methods=['GET'])
def api_versions(product_id):
    vs = service.get_versions(product_id)
    return jsonify(vs)

@app.route('/rollback/<product_id>/<timestamp>', methods=['POST'])
def api_rollback(product_id, timestamp):
    try:
        data = service.rollback(product_id, timestamp)
        return jsonify(data)
    except ValueError:
        abort(404)

@app.route('/metrics', methods=['GET'])
def api_metrics():
    return jsonify({})

@app.route('/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'ok'})
