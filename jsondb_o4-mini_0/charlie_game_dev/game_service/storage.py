import os
import json
import tempfile
import time
from .utils import encrypt, decrypt
from .journal import Journal
from .metrics import metrics
from .hooks import hooks

class GameStore:
    def __init__(self, store_dir, encryption_key=None, enable_journal=False):
        self.store_dir = store_dir
        self.data_path = os.path.join(store_dir, 'data.json')
        self.versions_dir = os.path.join(store_dir, 'versions')
        self.journal_path = os.path.join(store_dir, 'data.journal')
        os.makedirs(self.versions_dir, exist_ok=True)
        if enable_journal:
            self.journal = Journal(self.journal_path)
        else:
            self.journal = None
        self.key = encryption_key

    def load(self):
        start = time.time()
        if not os.path.exists(self.data_path):
            data = {}
        else:
            with open(self.data_path, 'rb') as f:
                b = f.read()
                if self.key:
                    b = decrypt(b, self.key)
                data = json.loads(b.decode('utf-8'))
        metrics.inc('load_latency', time.time() - start)
        return data

    def save(self, data):
        for fn in hooks.pre_write:
            data = fn(data)
        if self.journal:
            self.journal.append({'timestamp': time.time(), 'data': data})
        # versioning
        ver_files = [f for f in os.listdir(self.versions_dir) if f.endswith('.json')]
        versions = sorted(int(f.split('.')[0]) for f in ver_files) if ver_files else []
        ver = versions[-1] + 1 if versions else 1
        ver_path = os.path.join(self.versions_dir, f'{ver}.json')
        with open(ver_path, 'w') as vf:
            json.dump(data, vf)
        # atomic write
        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.store_dir)
        with os.fdopen(tmp_fd, 'wb') as tmp:
            b = json.dumps(data).encode('utf-8')
            if self.key:
                b = encrypt(b, self.key)
            tmp.write(b)
        os.replace(tmp_path, self.data_path)
        for fn in hooks.post_write:
            fn(data)
        metrics.inc('save_latency', 1)

    def batch_upsert(self, items, key_field='id'):
        data = self.load()
        for item in items:
            idx = item[key_field]
            data[idx] = data.get(idx, {})
            data[idx].update(item)
        self.save(data)

    def soft_delete(self, key):
        data = self.load()
        if key in data:
            data[key]['deleted'] = True
            self.save(data)

    def undelete(self, key):
        data = self.load()
        if key in data and data[key].get('deleted'):
            data[key]['deleted'] = False
            self.save(data)

    def update_item(self, key, item):
        data = self.load()
        data[key] = data.get(key, {})
        data[key].update(item)
        self.save(data)

    def revert(self, version):
        ver_path = os.path.join(self.versions_dir, f'{version}.json')
        if not os.path.exists(ver_path):
            return False
        with open(ver_path) as vf:
            data = json.load(vf)
        self.save(data)
        return True
