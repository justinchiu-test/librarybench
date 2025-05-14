import time
import threading
import copy
import os
import json
import shutil
from datetime import datetime, timedelta

class DocumentNotFoundError(Exception):
    pass

class VersionConflictError(Exception):
    pass

class BatchUpsertError(Exception):
    pass

def _deep_merge(a, b):
    result = copy.deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result

class InMemoryBackend:
    def __init__(self):
        self._store = {}

    def load(self, key):
        if key not in self._store:
            raise DocumentNotFoundError(f"Key '{key}' not found")
        entry = self._store[key]
        return copy.deepcopy(entry['document']), copy.deepcopy(entry['metadata'])

    def save(self, key, document, metadata):
        self._store[key] = {
            'document': copy.deepcopy(document),
            'metadata': copy.deepcopy(metadata)
        }

    def delete(self, key):
        if key in self._store:
            del self._store[key]

    def list_keys(self):
        return list(self._store.keys())

    def backup(self):
        return copy.deepcopy(self._store)

    def restore(self, backup_data):
        self._store = copy.deepcopy(backup_data)

class FileSystemBackend:
    def __init__(self, base_path, encryptor=None):
        self.base_path = base_path
        self.encryptor = encryptor
        os.makedirs(self.base_path, exist_ok=True)

    def _key_path(self, key):
        safe = key.replace('/', '_')
        return os.path.join(self.base_path, safe + '.json')

    def load(self, key):
        path = self._key_path(key)
        if not os.path.exists(path):
            raise DocumentNotFoundError(f"Key '{key}' not found")
        with open(path, 'rb') as f:
            data = f.read()
            if self.encryptor:
                data = self.encryptor.decrypt(data)
            obj = json.loads(data.decode('utf-8'))
            return obj['document'], obj['metadata']

    def save(self, key, document, metadata):
        path = self._key_path(key)
        obj = {'document': document, 'metadata': metadata}
        data = json.dumps(obj).encode('utf-8')
        if self.encryptor:
            data = self.encryptor.encrypt(data)
        with open(path, 'wb') as f:
            f.write(data)

    def delete(self, key):
        path = self._key_path(key)
        if os.path.exists(path):
            os.remove(path)

    def list_keys(self):
        files = os.listdir(self.base_path)
        keys = []
        for fn in files:
            if fn.endswith('.json'):
                keys.append(fn[:-5].replace('_', '/'))
        return keys

    def backup(self):
        tmp = self.base_path + '_backup_' + str(int(time.time()))
        shutil.copytree(self.base_path, tmp)
        return tmp

    def restore(self, backup_path):
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)
        shutil.copytree(backup_path, self.base_path)

class DummyEncryptor:
    def __init__(self, passphrase):
        self.passphrase = passphrase
    def encrypt(self, data):
        return data
    def decrypt(self, data):
        return data

class EdgeJSONDB:
    def __init__(self, storage_backend='memory', **params):
        self._lock = threading.Lock()
        self._ttl = None
        self._stream_callbacks = []
        self._plugins = {}
        # control whether plugin errors are suppressed
        self._suppress_plugin_errors = True
        self._encryption = None
        self.set_storage_backend(storage_backend, **params)

    def set_storage_backend(self, backend_type, **params):
        if backend_type == 'memory':
            self._storage = InMemoryBackend()
        elif backend_type == 'fs':
            encryptor = None
            if self._encryption:
                encryptor = DummyEncryptor(self._encryption)
            base_path = params.get('base_path', './data')
            self._storage = FileSystemBackend(base_path, encryptor)
        elif backend_type == 's3':
            raise NotImplementedError("S3 backend not implemented")
        else:
            raise ValueError("Unknown backend type")
    
    def set_ttl(self, seconds):
        self._ttl = seconds

    def cleanup_expired(self):
        if self._ttl is None:
            return
        now = datetime.utcnow()
        keys = self._storage.list_keys()
        for key in keys:
            try:
                _, metadata = self._storage.load(key)
                updated = metadata.get('updated_at', metadata.get('created_at'))
                if isinstance(updated, str):
                    updated = datetime.fromisoformat(updated)
                if (now - updated).total_seconds() > self._ttl:
                    self._storage.delete(key)
                    self._on_change('expire', key, None)
            except DocumentNotFoundError:
                continue

    def register_plugin(self, name, plugin):
        self._plugins[name] = plugin

    def stream_changes(self, callback):
        self._stream_callbacks.append(callback)

    def encrypt_at_rest(self, passphrase):
        self._encryption = passphrase
        # reinitialize fs backend if used
        if isinstance(self._storage, FileSystemBackend):
            self.set_storage_backend('fs', base_path=self._storage.base_path)

    def _on_change(self, event_type, key, document, metadata=None):
        # notify streaming callbacks
        for cb in self._stream_callbacks:
            try:
                cb(event_type, key, copy.deepcopy(document))
            except Exception:
                pass
        # notify plugins
        for plugin in self._plugins.values():
            hook = getattr(plugin, f'on_{event_type}', None)
            if callable(hook):
                if self._suppress_plugin_errors:
                    try:
                        hook(key, copy.deepcopy(document), metadata)
                    except Exception:
                        pass
                else:
                    # in batch mode, let plugin errors propagate
                    hook(key, copy.deepcopy(document), metadata)

    def insert_document(self, key, document):
        with self._lock:
            try:
                self._storage.load(key)
                raise ValueError(f"Key '{key}' already exists")
            except DocumentNotFoundError:
                now = datetime.utcnow()
                metadata = {
                    'version': 1,
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                    'history': [
                        {'version': 1, 'timestamp': now.isoformat(), 'document': copy.deepcopy(document)}
                    ]
                }
                self._storage.save(key, document, metadata)
                self._on_change('insert', key, document, metadata)

    def get_document(self, key):
        document, _ = self._storage.load(key)
        return document

    def get_metadata(self, key):
        _, metadata = self._storage.load(key)
        return metadata

    def get_versions(self, key):
        _, metadata = self._storage.load(key)
        return metadata.get('history', [])

    def update_document(self, key, patch, full_replace=False, expected_version=None):
        with self._lock:
            document, metadata = self._storage.load(key)
            if expected_version is not None and metadata.get('version') != expected_version:
                raise VersionConflictError("Version mismatch")
            if full_replace:
                new_doc = copy.deepcopy(patch)
            else:
                new_doc = _deep_merge(document, patch)
            new_version = metadata['version'] + 1
            now = datetime.utcnow()
            metadata['version'] = new_version
            metadata['updated_at'] = now.isoformat()
            metadata['history'].append({
                'version': new_version,
                'timestamp': now.isoformat(),
                'document': copy.deepcopy(new_doc)
            })
            self._storage.save(key, new_doc, metadata)
            self._on_change('update', key, new_doc, metadata)

    def rollback(self, key, version):
        with self._lock:
            _, metadata = self._storage.load(key)
            history = metadata.get('history', [])
            rec = next((h for h in history if h['version'] == version), None)
            if rec is None:
                raise ValueError("Version not found")
            doc = copy.deepcopy(rec['document'])
            new_version = metadata['version'] + 1
            now = datetime.utcnow()
            metadata['version'] = new_version
            metadata['updated_at'] = now.isoformat()
            metadata['history'].append({
                'version': new_version,
                'timestamp': now.isoformat(),
                'document': copy.deepcopy(doc)
            })
            self._storage.save(key, doc, metadata)
            self._on_change('rollback', key, doc, metadata)

    def batch_upsert(self, docs):
        with self._lock:
            # backup current state
            backup = self._storage.backup()
            # enable strict plugin error propagation
            old_flag = self._suppress_plugin_errors
            self._suppress_plugin_errors = False
            try:
                for key, doc in docs.items():
                    try:
                        existing, meta = self._storage.load(key)
                        # update existing
                        new_version = meta['version'] + 1
                        now = datetime.utcnow()
                        meta['version'] = new_version
                        meta['updated_at'] = now.isoformat()
                        meta['history'].append({
                            'version': new_version,
                            'timestamp': now.isoformat(),
                            'document': copy.deepcopy(doc)
                        })
                        self._storage.save(key, doc, meta)
                        self._on_change('update', key, doc, meta)
                    except DocumentNotFoundError:
                        # insert new
                        now = datetime.utcnow()
                        md = {
                            'version': 1,
                            'created_at': now.isoformat(),
                            'updated_at': now.isoformat(),
                            'history': [
                                {'version': 1, 'timestamp': now.isoformat(), 'document': copy.deepcopy(doc)}
                            ]
                        }
                        self._storage.save(key, doc, md)
                        self._on_change('insert', key, doc, md)
            except Exception as e:
                # restore previous state on failure
                self._storage.restore(backup)
                raise BatchUpsertError("Batch upsert failed") from e
            finally:
                # restore plugin error handling preference
                self._suppress_plugin_errors = old_flag

    def backup(self):
        return self._storage.backup()

    def restore(self, backup_data):
        self._storage.restore(backup_data)
        # stream restore event
        for key in self._storage.list_keys():
            doc, _ = self._storage.load(key)
            self._on_change('restore', key, doc)
