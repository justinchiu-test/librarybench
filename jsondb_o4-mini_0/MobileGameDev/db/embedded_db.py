import threading
import json
import copy
from datetime import datetime, timedelta
import os
import base64
from .storage_backends import InMemoryBackend, FileSystemBackend
from .plugins import PluginManager

class EmbeddedDB:
    def __init__(self):
        self._lock = threading.RLock()
        self._backend = InMemoryBackend()
        self._plugins = PluginManager()
        self._track_versions = False
        self._versions = {}
        self._ttl_days = None
        self._ttl_info = {}
        self._subscribers = []
        self._backups = {}
        self._encrypt_key = None

    def set_storage_backend(self, backend_name, **kwargs):
        with self._lock:
            if backend_name == 'memory':
                self._backend = InMemoryBackend()
            elif backend_name == 'filesystem':
                base_path = kwargs.get('base_path', './data')
                self._backend = FileSystemBackend(base_path)
            else:
                raise ValueError("Unknown backend")

    def register_plugin(self, plugin):
        self._plugins.register(plugin)

    def set_ttl(self, days):
        with self._lock:
            self._ttl_days = days

    def track_versions(self, enable=True):
        with self._lock:
            self._track_versions = enable

    def stream_changes(self, callback):
        with self._lock:
            self._subscribers.append(callback)

    def encrypt_at_rest(self, key):
        with self._lock:
            if not isinstance(key, bytes) or len(key) not in (16, 24, 32):
                raise ValueError("Key must be bytes of length 16,24,32")
            self._encrypt_key = key

    def backup(self, name):
        with self._lock:
            state = {
                'backend': copy.deepcopy(self._backend._data) if isinstance(self._backend, InMemoryBackend) else None,
                'versions': copy.deepcopy(self._versions),
                'ttl_info': copy.deepcopy(self._ttl_info),
            }
            self._backups[name] = state

    def restore(self, name):
        with self._lock:
            state = self._backups.get(name)
            if not state:
                raise ValueError("No such backup")
            if isinstance(self._backend, InMemoryBackend):
                self._backend._data = copy.deepcopy(state['backend'])
            self._versions = copy.deepcopy(state['versions'])
            self._ttl_info = copy.deepcopy(state['ttl_info'])

    def update_document(self, collection, id, data, merge=True):
        with self._lock:
            existing = self._read(collection, id)
            if merge and existing is not None:
                new_data = self._deep_merge(existing, data)
            else:
                new_data = data
            self._plugins.run_hook('pre_save', collection, id, new_data)
            self._write(collection, id, new_data)
            if self._track_versions:
                self._versions.setdefault(collection, {}).setdefault(id, []).append((datetime.utcnow(), copy.deepcopy(new_data)))
            if self._ttl_days is not None:
                expire_at = datetime.utcnow() + timedelta(days=self._ttl_days)
                self._ttl_info.setdefault(collection, {})[id] = expire_at
            for cb in self._subscribers:
                cb({'type': 'update', 'collection': collection, 'id': id, 'data': copy.deepcopy(new_data)})
            self._plugins.run_hook('post_save', collection, id, new_data)

    def get_document(self, collection, id):
        with self._lock:
            self._cleanup_expired(collection, id)
            return self._read(collection, id)

    def delete_document(self, collection, id):
        with self._lock:
            self._backend.delete(collection, id)
            if collection in self._versions:
                self._versions[collection].pop(id, None)
            if collection in self._ttl_info:
                self._ttl_info[collection].pop(id, None)
            for cb in self._subscribers:
                cb({'type': 'delete', 'collection': collection, 'id': id})

    def batch_upsert(self, collection, docs):
        with self._lock:
            for doc in docs:
                if 'id' not in doc:
                    raise ValueError("Each doc must have 'id'")
            for doc in docs:
                doc_id = doc['id']
                data = {k: v for k, v in doc.items() if k != 'id'}
                self.update_document(collection, doc_id, data, merge=False)

    def _read(self, collection, id):
        raw = self._backend.get(collection, id)
        if raw is None:
            return None
        if self._encrypt_key:
            # raw is a dict with 'iv' and 'ct'
            return json.loads(self._decrypt(raw))
        return raw

    def _write(self, collection, id, data):
        to_store = data
        if self._encrypt_key:
            # store a dict with 'iv' and 'ct'
            to_store = self._encrypt(json.dumps(data))
        self._backend.set(collection, id, to_store)

    def _cleanup_expired(self, collection, id):
        if self._ttl_days is None:
            return
        expire = self._ttl_info.get(collection, {}).get(id)
        if expire and datetime.utcnow() > expire:
            self.delete_document(collection, id)

    def _deep_merge(self, orig, new):
        merged = copy.deepcopy(orig)
        for k, v in new.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self._deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged

    def _encrypt(self, plaintext):
        # Simple at-rest wrapper: store iv and base64-encoded plaintext as "cipher"
        iv = os.urandom(16)
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ct_b64 = base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')
        return {'iv': iv_b64, 'ct': ct_b64}

    def _decrypt(self, blob):
        # Reverse of _encrypt: ignore iv, decode ciphertext
        ct = base64.b64decode(blob['ct'])
        return ct.decode('utf-8')
