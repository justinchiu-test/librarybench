import os
import json
import threading

class StorageBackend:
    def get(self, collection, id):
        raise NotImplementedError

    def set(self, collection, id, data):
        raise NotImplementedError

    def delete(self, collection, id):
        raise NotImplementedError

    def list_collections(self):
        raise NotImplementedError

    def list_ids(self, collection):
        raise NotImplementedError

class InMemoryBackend(StorageBackend):
    def __init__(self):
        self._data = {}
        self._lock = threading.RLock()

    def get(self, collection, id):
        with self._lock:
            return self._data.get(collection, {}).get(id)

    def set(self, collection, id, data):
        with self._lock:
            self._data.setdefault(collection, {})[id] = data

    def delete(self, collection, id):
        with self._lock:
            if collection in self._data and id in self._data[collection]:
                del self._data[collection][id]

    def list_collections(self):
        with self._lock:
            return list(self._data.keys())

    def list_ids(self, collection):
        with self._lock:
            return list(self._data.get(collection, {}).keys())

class FileSystemBackend(StorageBackend):
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        self._lock = threading.RLock()

    def _get_path(self, collection, id):
        dir_path = os.path.join(self.base_path, collection)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, f"{id}.json")

    def get(self, collection, id):
        path = self._get_path(collection, id)
        if not os.path.exists(path):
            return None
        with self._lock, open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def set(self, collection, id, data):
        path = self._get_path(collection, id)
        with self._lock, open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def delete(self, collection, id):
        path = self._get_path(collection, id)
        with self._lock:
            if os.path.exists(path):
                os.remove(path)

    def list_collections(self):
        with self._lock:
            return [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]

    def list_ids(self, collection):
        dir_path = os.path.join(self.base_path, collection)
        with self._lock:
            if not os.path.exists(dir_path):
                return []
            return [os.path.splitext(f)[0] for f in os.listdir(dir_path) if f.endswith('.json')]
