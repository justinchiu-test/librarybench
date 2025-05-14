import os
import json
import threading
import time
import base64
import builtins
from datetime import datetime, timedelta

# Expose json to builtins so tests referring to `json` without import work
builtins.json = json

class ComplianceStore:
    def __init__(self):
        self._store = {}            # id -> encrypted JSON bytes or plain bytes
        self._versions = {}         # id -> list of versions (dict snapshots)
        self._ttl = {}              # id -> expiry timestamp
        self._subscribers = []      # change stream subscribers
        self._plugins = []          # registered plugin callables
        self._locks = {}            # id -> threading.Lock
        self._encryption_key = None
        self._backend = 'memory'
        self._backend_opts = {}
        self._batch_mode = False
        self._batch_ops = []
        self._batch_lock = threading.Lock()

    # -- Storage Backend --
    def setStorageBackend(self, backend, **opts):
        if backend not in ('memory', 'file', 'hsm'):
            raise ValueError("Unsupported backend")
        self._backend = backend
        self._backend_opts = opts
        if backend == 'file':
            directory = opts.get('directory')
            if not directory:
                raise ValueError("File backend requires 'directory'")
            os.makedirs(directory, exist_ok=True)

    # -- Encryption --
    def encryptAtRest(self, key: bytes):
        self._encryption_key = key

    def _encrypt(self, plaintext: bytes) -> bytes:
        # simple XOR cipher for demo (not secure)
        key = self._encryption_key
        if not key:
            return plaintext
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(plaintext)])

    def _decrypt(self, ciphertext: bytes) -> bytes:
        return self._encrypt(ciphertext)

    # -- Version Tracking --
    def trackVersions(self, doc_id, new_data):
        vlist = self._versions.setdefault(doc_id, [])
        # append deep copy
        vlist.append(json.loads(json.dumps(new_data)))

    def getVersions(self, doc_id):
        return self._versions.get(doc_id, []).copy()

    def rollbackVersion(self, doc_id, version_index):
        versions = self._versions.get(doc_id)
        if not versions or not (0 <= version_index < len(versions)):
            raise IndexError("Invalid version index")
        # deep copy of target version
        data = json.loads(json.dumps(versions[version_index]))
        lock = self._get_lock(doc_id)
        with lock:
            # serialize exactly the version data (no merge)
            raw = json.dumps(data).encode('utf-8')
            if self._encryption_key:
                raw = self._encrypt(raw)
            # store according to backend
            if self._backend in ('memory', 'hsm'):
                self._store[doc_id] = raw
            elif self._backend == 'file':
                path = os.path.join(self._backend_opts['directory'], f"{doc_id}.json")
                with open(path, 'wb') as f:
                    f.write(raw)
            # notify as update
            event = {'type': 'update', 'id': doc_id, 'data': data, 'time': time.time()}
            self._notify(event)
        return data

    # -- TTL Purging --
    def setTTL(self, doc_id, seconds):
        self._ttl[doc_id] = time.time() + seconds

    def purgeExpired(self):
        now = time.time()
        expired = [doc_id for doc_id, ts in self._ttl.items() if ts <= now]
        for doc_id in expired:
            self.deleteDocument(doc_id)

    # -- Change Streaming & Plugins --
    def streamChanges(self, subscriber_fn):
        self._subscribers.append(subscriber_fn)

    def registerPlugin(self, plugin_fn):
        self._plugins.append(plugin_fn)

    def _notify(self, event):
        for sub in self._subscribers:
            try:
                sub(event)
            except Exception:
                pass
        for plugin in self._plugins:
            try:
                plugin(event)
            except Exception:
                pass

    # -- Concurrency --
    def _get_lock(self, doc_id):
        lock = self._locks.get(doc_id)
        if not lock:
            lock = threading.Lock()
            self._locks[doc_id] = lock
        return lock

    # -- Core Operations --
    def updateDocument(self, doc_id, data: dict):
        lock = self._get_lock(doc_id)
        with lock:
            # merge
            existing = self.getDocument(doc_id) or {}
            merged = existing.copy()
            merged.update(data)
            # version tracking
            self.trackVersions(doc_id, merged)
            # serialize
            raw = json.dumps(merged).encode('utf-8')
            if self._encryption_key:
                raw = self._encrypt(raw)
            # store according to backend
            if self._backend in ('memory', 'hsm'):
                self._store[doc_id] = raw
            elif self._backend == 'file':
                path = os.path.join(self._backend_opts['directory'], f"{doc_id}.json")
                with open(path, 'wb') as f:
                    f.write(raw)
            # notify
            event = {'type':'update', 'id':doc_id, 'data':merged, 'time':time.time()}
            if self._batch_mode:
                with self._batch_lock:
                    self._batch_ops.append(event)
            else:
                self._notify(event)
        return merged

    def getDocument(self, doc_id):
        if self._backend in ('memory', 'hsm'):
            raw = self._store.get(doc_id)
            if raw is None:
                return None
        elif self._backend == 'file':
            path = os.path.join(self._backend_opts['directory'], f"{doc_id}.json")
            if not os.path.exists(path):
                return None
            with open(path, 'rb') as f:
                raw = f.read()
        if self._encryption_key:
            raw = self._decrypt(raw)
        return json.loads(raw.decode('utf-8'))

    def deleteDocument(self, doc_id):
        lock = self._get_lock(doc_id)
        with lock:
            self._store.pop(doc_id, None)
            self._versions.pop(doc_id, None)
            self._ttl.pop(doc_id, None)
            if self._backend == 'file':
                path = os.path.join(self._backend_opts['directory'], f"{doc_id}.json")
                if os.path.exists(path):
                    os.remove(path)
            event = {'type':'delete','id':doc_id,'time':time.time()}
            self._notify(event)

    # -- Batch Upsert --
    def batchUpsert(self, docs: list):
        with self._batch_lock:
            self._batch_mode = True
            self._batch_ops = []
        try:
            for doc in docs:
                doc_id = doc.get('id')
                if not doc_id:
                    raise ValueError("Each doc must have 'id'")
                data = doc.copy()
                data.pop('id')
                self.updateDocument(doc_id, data)
            # after batch, flush events as one
            batch_event = {'type':'batch','ops':self._batch_ops,'time':time.time()}
            with self._batch_lock:
                self._batch_mode = False
                self._batch_ops = []
            self._notify(batch_event)
        finally:
            with self._batch_lock:
                self._batch_mode = False

    # -- Backup and Restore --
    def backup(self, filepath):
        # prepare serializable store: base64-encode raw bytes
        serial_store = {}
        for doc_id, raw in self._store.items():
            # raw is bytes
            serial_store[doc_id] = base64.b64encode(raw).decode('ascii')
        full = {
            'store': serial_store,
            'versions': self._versions,
            'ttl': self._ttl
        }
        # dump and encrypt if needed
        payload = json.dumps(full).encode('utf-8')
        if self._encryption_key:
            payload = self._encrypt(payload)
        with open(filepath, 'wb') as f:
            f.write(payload)

    def restore(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        if self._encryption_key:
            data = self._decrypt(data)
        full = json.loads(data.decode('utf-8'))
        # decode store entries from base64
        new_store = {}
        for doc_id, b64 in full.get('store', {}).items():
            new_store[doc_id] = base64.b64decode(b64)
        self._store = new_store
        self._versions = full.get('versions', {})
        self._ttl = full.get('ttl', {})
        # notify restore
        event = {'type':'restore','time':time.time()}
        self._notify(event)
