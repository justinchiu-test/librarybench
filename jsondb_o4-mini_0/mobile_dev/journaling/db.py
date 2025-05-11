import os
import json
import time
import tempfile
from .schema import validate_entry, SchemaError
from .crypto import AESCipher
from .plugins import PluginManager

class JournalDB:
    def __init__(self, directory, key, ttl_days=30):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.cipher = AESCipher(key)
        self.ttl_seconds = ttl_days * 24 * 3600
        self.entries = {}
        self.index = {}
        self.plugin_manager = PluginManager()
        self._load_entries()
        self.sweep()

    def _load_entries(self):
        for filename in os.listdir(self.directory):
            if not filename.endswith('.enc'):
                continue
            path = os.path.join(self.directory, filename)
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                raw = self.cipher.decrypt(data)
                entry = json.loads(raw.decode('utf-8'))
                validate_entry(entry)
                self.entries[entry['id']] = entry
                for tag in entry.get('tags', []):
                    self.index.setdefault(tag, set()).add(entry['id'])
            except Exception:
                continue

    def registerPlugin(self, plugin):
        self.plugin_manager.register(plugin)

    def createIndex(self):
        self.index.clear()
        for entry in self.entries.values():
            for tag in entry.get('tags', []):
                self.index.setdefault(tag, set()).add(entry['id'])

    def sweep(self):
        now = time.time()
        to_delete = []
        for eid, entry in list(self.entries.items()):
            if 'draft' in entry.get('tags', []) and (now - entry['created_at']) > self.ttl_seconds:
                to_delete.append(eid)
        for eid in to_delete:
            self.delete_by_id(eid)

    def persistAtomically(self, filepath, data_bytes):
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=dirpath)
        try:
            with os.fdopen(fd, 'wb') as tmp_file:
                tmp_file.write(data_bytes)
            os.replace(tmp_path, filepath)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def upsert(self, entry):
        validate_entry(entry)
        self.plugin_manager.apply_hook('on_before_upsert', entry)
        now = time.time()
        if entry['id'] in self.entries:
            entry['created_at'] = self.entries[entry['id']]['created_at']
        else:
            entry['created_at'] = now
        entry['updated_at'] = now
        old_tags = set(self.entries.get(entry['id'], {}).get('tags', []))
        new_tags = set(entry.get('tags', []))
        for tag in old_tags - new_tags:
            self.index.get(tag, set()).discard(entry['id'])
        for tag in new_tags - old_tags:
            self.index.setdefault(tag, set()).add(entry['id'])
        filepath = os.path.join(self.directory, f"{entry['id']}.json.enc")
        raw = json.dumps(entry).encode('utf-8')
        encrypted = self.cipher.encrypt(raw)
        self.persistAtomically(filepath, encrypted)
        self.entries[entry['id']] = entry.copy()
        self.plugin_manager.apply_hook('on_after_upsert', entry)

    def batchUpsert(self, entries):
        # Snapshot in-memory state
        from copy import deepcopy
        entries_backup = deepcopy(self.entries)
        index_backup = {tag: set(ids) for tag, ids in self.index.items()}
        try:
            for entry in entries:
                self.upsert(entry)
        except Exception:
            # Roll back in-memory state
            self.entries = entries_backup
            self.index = index_backup
            raise

    def delete_by_id(self, eid):
        entry = self.entries.pop(eid, None)
        if entry:
            for tag in entry.get('tags', []):
                self.index.get(tag, set()).discard(eid)
            filepath = os.path.join(self.directory, f"{eid}.json.enc")
            if os.path.exists(filepath):
                os.remove(filepath)
            self.plugin_manager.apply_hook('on_delete', entry)

    def delete(self, filter_fn):
        for eid, entry in list(self.entries.items()):
            if filter_fn(entry):
                self.delete_by_id(eid)

    def softDelete(self, eid):
        entry = self.entries.get(eid)
        if not entry:
            return
        entry['deleted'] = True
        entry['deleted_at'] = time.time()
        self.upsert(entry)

    def purge(self, eid):
        self.delete_by_id(eid)

    def deleteDraftsOlderThan(self, days):
        cutoff = time.time() - days*24*3600
        self.delete(lambda e: 'draft' in e.get('tags', []) and e['created_at'] < cutoff)

    def startRestServer(self, port):
        from .server import make_app
        app = make_app(self)
        import threading
        t = threading.Thread(target=app.serve_forever, daemon=True)
        t.start()
        return app
