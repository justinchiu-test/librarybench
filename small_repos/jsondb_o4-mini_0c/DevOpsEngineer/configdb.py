import threading
import time
import pickle
import os
import copy

class ConcurrencyError(Exception):
    pass

class ValidationError(Exception):
    pass

class StorageBackend:
    def load(self, key):
        raise NotImplementedError
    def save(self, key, data):
        raise NotImplementedError
    def delete(self, key):
        raise NotImplementedError
    def list_keys(self):
        raise NotImplementedError

class InMemoryBackend(StorageBackend):
    def __init__(self):
        self.store = {}
    def load(self, key):
        return self.store.get(key)
    def save(self, key, data):
        self.store[key] = data
    def delete(self, key):
        if key in self.store:
            del self.store[key]
    def list_keys(self):
        return list(self.store.keys())

class ConfigDB:
    def __init__(self, backend=None, sweep_interval=1):
        self.backend = backend or InMemoryBackend()
        self.ttl_map = {}  # key -> expiry timestamp
        self.version_map = {}  # key -> list of versions
        self.locks = {}  # key -> threading.Lock
        self.plugins = []
        self.change_listeners = []
        self._stop_sweeper = threading.Event()
        self.sweep_interval = sweep_interval
        self.sweeper_thread = threading.Thread(target=self._sweeper, daemon=True)
        self.sweeper_thread.start()

    def setStorageBackend(self, backend):
        self.backend = backend

    def registerPlugin(self, plugin):
        self.plugins.append(plugin)

    def streamChanges(self, listener):
        self.change_listeners.append(listener)

    def setTTL(self, key, ttl_seconds):
        if key in self.version_map:
            self.ttl_map[key] = time.time() + ttl_seconds

    def createDocument(self, key, doc, ttl=None, lock_type='optimistic'):
        if self.backend.load(key) is not None:
            raise KeyError(f"Document {key} exists")
        now = time.time()
        version_entry = {'version': 1, 'timestamp': now, 'doc': copy.deepcopy(doc)}
        self.version_map[key] = [version_entry]
        self.backend.save(key, copy.deepcopy(doc))
        if ttl is not None:
            self.ttl_map[key] = now + ttl
        self.locks.setdefault(key, threading.Lock())
        self._notify_listeners({'action': 'create', 'key': key, 'doc': copy.deepcopy(doc), 'version':1})

    def getDocument(self, key, with_versions=False):
        doc = self.backend.load(key)
        if doc is None:
            return None
        if with_versions:
            return copy.deepcopy(doc), copy.deepcopy(self.version_map.get(key, []))
        return copy.deepcopy(doc)

    def updateDocument(self, key, doc, merge=True, lock_type='optimistic', expected_version=None):
        existing = self.backend.load(key)
        if existing is None:
            raise KeyError(f"Document {key} does not exist")
        lock = self.locks.setdefault(key, threading.Lock())
        # pessimistic locking
        if lock_type == 'pessimistic':
            acquired = lock.acquire(blocking=False)
            if not acquired:
                raise ConcurrencyError("Could not acquire lock")
        # optimistic version check
        current_version = self.version_map[key][-1]['version']
        if expected_version is not None and expected_version != current_version:
            if lock_type == 'pessimistic':
                lock.release()
            raise ConcurrencyError("Version mismatch")
        new_doc = copy.deepcopy(existing)
        if merge and isinstance(existing, dict) and isinstance(doc, dict):
            new_doc.update(doc)
        else:
            new_doc = copy.deepcopy(doc)
        # plugins before_update
        for p in self.plugins:
            if hasattr(p, 'before_update'):
                p.before_update(key, existing, new_doc)
        new_version = current_version + 1
        now = time.time()
        self.version_map[key].append({'version': new_version, 'timestamp': now, 'doc': copy.deepcopy(new_doc)})
        self.backend.save(key, copy.deepcopy(new_doc))
        # plugins after_update
        for p in self.plugins:
            if hasattr(p, 'after_update'):
                p.after_update(key, new_doc)
        if lock_type == 'pessimistic':
            lock.release()
        self._notify_listeners({'action': 'update', 'key': key, 'doc': copy.deepcopy(new_doc), 'version':new_version})
        return new_doc

    def deleteDocument(self, key):
        if self.backend.load(key) is None:
            return
        self.backend.delete(key)
        self.version_map.pop(key, None)
        self.ttl_map.pop(key, None)
        self.locks.pop(key, None)
        self._notify_listeners({'action': 'delete', 'key': key})

    def batchUpsert(self, items):
        backup_versions = copy.deepcopy(self.version_map)
        backup_storage = {}
        for key in self.backend.list_keys():
            backup_storage[key] = copy.deepcopy(self.backend.load(key))
        try:
            for key, doc in items:
                if self.backend.load(key) is None:
                    self.createDocument(key, doc)
                else:
                    self.updateDocument(key, doc)
        except Exception as e:
            # rollback
            for key, data in backup_storage.items():
                self.backend.save(key, data)
            for key in list(self.backend.list_keys()):
                if key not in backup_storage:
                    self.backend.delete(key)
            self.version_map = backup_versions
            raise
        return True

    def backup(self, path):
        data = {
            'storage': {k: self.backend.load(k) for k in self.backend.list_keys()},
            'versions': self.version_map,
            'ttls': self.ttl_map
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def restore(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        # clear existing
        for k in self.backend.list_keys():
            self.backend.delete(k)
        self.version_map = {}
        self.ttl_map = {}
        # restore
        for k, doc in data['storage'].items():
            self.backend.save(k, doc)
        self.version_map = data['versions']
        self.ttl_map = data['ttls']

    def rollback(self, key, version):
        if key not in self.version_map:
            raise KeyError("No such document")
        versions = self.version_map[key]
        for entry in versions:
            if entry['version'] == version:
                self.backend.save(key, copy.deepcopy(entry['doc']))
                # truncate versions
                idx = versions.index(entry)
                self.version_map[key] = versions[:idx+1]
                self._notify_listeners({'action': 'rollback', 'key': key, 'version':version})
                return
        raise KeyError("Version not found")

    def _notify_listeners(self, event):
        for listener in self.change_listeners:
            try:
                listener(event)
            except Exception:
                pass

    def _sweeper(self):
        while not self._stop_sweeper.is_set():
            now = time.time()
            to_delete = [k for k, exp in list(self.ttl_map.items()) if exp <= now]
            for k in to_delete:
                self.deleteDocument(k)
            time.sleep(self.sweep_interval)

    def close(self):
        self._stop_sweeper.set()
        self.sweeper_thread.join(timeout=1)
