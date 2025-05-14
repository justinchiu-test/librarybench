import os
import json
import tempfile
import threading
import shutil
import base64
import time

class DocumentStore:
    def __init__(self, base_dir, encryption_key, journaling=False):
        self.base_dir = base_dir
        self.key = encryption_key
        self.journaling = journaling
        self.pre_hooks = []
        self.post_hooks = []
        self.metrics = {'create': 0, 'read': 0, 'update': 0, 'delete': 0, 'batch_upsert': 0}
        self.lock = threading.Lock()
        if journaling:
            os.makedirs(self.base_dir, exist_ok=True)
            self.journal_file = os.path.join(self.base_dir, 'journal.log')

    def _record_dir(self, record_id):
        return os.path.join(self.base_dir, record_id)

    def _version_dir(self, record_id):
        return os.path.join(self._record_dir(record_id), 'versions')

    def _current_dir(self, record_id):
        return os.path.join(self._record_dir(record_id), 'current')

    def _ensure_dirs(self, record_id):
        for d in (self._record_dir(record_id), self._version_dir(record_id), self._current_dir(record_id)):
            os.makedirs(d, exist_ok=True)

    def _encrypt(self, data):
        payload = json.dumps(data).encode('utf-8')
        return base64.b64encode(payload)

    def _decrypt(self, data_bytes):
        return json.loads(base64.b64decode(data_bytes).decode('utf-8'))

    def _atomic_write(self, path, data_bytes):
        dirpath = os.path.dirname(path)
        fd, tmp_path = tempfile.mkstemp(dir=dirpath)
        with os.fdopen(fd, 'wb') as tmp_file:
            tmp_file.write(data_bytes)
        os.replace(tmp_path, path)

    def _record_path(self, record_id, version):
        return os.path.join(self._version_dir(record_id), f'v{version}.json.enc')

    def _current_path(self, record_id):
        return os.path.join(self._current_dir(record_id), 'current.json.enc')

    def _append_journal(self, op, record_id, data):
        entry = json.dumps({'op': op, 'id': record_id, 'data': data, 'timestamp': time.time()})
        with open(self.journal_file, 'a') as f:
            f.write(entry + '\n')

    def create_record(self, record_id, data):
        with self.lock:
            self._ensure_dirs(record_id)
            new = data.copy()
            new['_version'] = 1
            new['_deleted'] = False
            for hook in self.pre_hooks:
                hook(record_id, new)
            enc = self._encrypt(new)
            p1 = self._record_path(record_id, 1)
            p2 = self._current_path(record_id)
            self._atomic_write(p1, enc)
            self._atomic_write(p2, enc)
            if self.journaling:
                self._append_journal('create', record_id, new)
            self.metrics['create'] += 1

    def read_record(self, record_id, version=None):
        self.metrics['read'] += 1
        if version is None:
            path = self._current_path(record_id)
        else:
            path = self._record_path(record_id, version)
        if not os.path.exists(path):
            raise KeyError(f"Record {record_id} version {version} not found")
        data = self._decrypt(open(path, 'rb').read())
        return data

    def update_record(self, record_id, merge_data):
        with self.lock:
            current = self.read_record(record_id)
            if current.get('_deleted'):
                raise KeyError(f"Record {record_id} is deleted")
            new = current.copy()
            new.update(merge_data)
            new['_version'] = current['_version'] + 1
            for hook in self.pre_hooks:
                hook(record_id, new)
            enc = self._encrypt(new)
            p1 = self._record_path(record_id, new['_version'])
            p2 = self._current_path(record_id)
            self._atomic_write(p1, enc)
            self._atomic_write(p2, enc)
            if self.journaling:
                self._append_journal('update', record_id, merge_data)
            self.metrics['update'] += 1
            for hook in self.post_hooks:
                hook('update', record_id, new)

    def delete_record(self, record_id):
        with self.lock:
            current = self.read_record(record_id)
            new = current.copy()
            new['_deleted'] = True
            new['_version'] = current['_version'] + 1
            for hook in self.pre_hooks:
                hook(record_id, new)
            enc = self._encrypt(new)
            p1 = self._record_path(record_id, new['_version'])
            p2 = self._current_path(record_id)
            self._atomic_write(p1, enc)
            self._atomic_write(p2, enc)
            if self.journaling:
                self._append_journal('delete', record_id, {})
            self.metrics['delete'] += 1

    def batch_upsert(self, records):
        with self.lock:
            self.metrics['batch_upsert'] += 1
            backup_dir = tempfile.mkdtemp()
            try:
                # backup
                shutil.copytree(self.base_dir, backup_dir, dirs_exist_ok=True)
                # apply
                for record_id, data in records:
                    if os.path.exists(self._record_dir(record_id)):
                        self.update_record(record_id, data)
                    else:
                        self.create_record(record_id, data)
            except Exception as e:
                # rollback
                for entry in os.listdir(self.base_dir):
                    path = os.path.join(self.base_dir, entry)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                shutil.copytree(backup_dir, self.base_dir, dirs_exist_ok=True)
                shutil.rmtree(backup_dir)
                raise
            shutil.rmtree(backup_dir)

    def rollback(self, record_id, version):
        with self.lock:
            data = self.read_record(record_id, version)
            new = data.copy()
            new['_version'] = version
            for hook in self.pre_hooks:
                hook(record_id, new)
            enc = self._encrypt(new)
            p = self._current_path(record_id)
            self._atomic_write(p, enc)

    def add_pre_hook(self, hook):
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook):
        self.post_hooks.append(hook)

    def metrics_snapshot(self):
        return dict(self.metrics)
