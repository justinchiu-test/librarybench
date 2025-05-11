import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from threading import Lock

from .encryption import Encryptor
from .schema import enforce_schema
from .plugins import PluginManager

class AuditDB:
    def __init__(self, data_dir, encryption_key: bytes, ttl_days=90):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.encr = Encryptor(encryption_key)
        self.ttl_days = ttl_days
        self.records = {}  # auditID -> record dict
        self.indexes = {"auditID": {}, "userID": {}, "eventSeverity": {}}
        self.plugins = PluginManager()
        self.lock = Lock()
        self._load_existing()

    def _load_existing(self):
        for fname in os.listdir(self.data_dir):
            if not fname.endswith(".enc"):
                continue
            path = os.path.join(self.data_dir, fname)
            with open(path, "rb") as f:
                data = f.read()
            try:
                pt = self.encr.decrypt(data)
                record = json.loads(pt.decode())
                self.records[record["auditID"]] = {"record": record, "path": path}
            except Exception:
                continue
        self._rebuild_indexes()

    def _rebuild_indexes(self):
        for field in self.indexes:
            self.indexes[field] = {}
        for aid, info in self.records.items():
            record = info["record"]
            for field in self.indexes:
                val = record.get(field)
                if val is None:
                    continue
                self.indexes[field].setdefault(val, set()).add(aid)

    def setTTL(self, days: int):
        self.ttl_days = days

    def createIndex(self, field: str):
        if field not in self.indexes:
            self.indexes[field] = {}
        self._rebuild_indexes()

    def registerPlugin(self, hook_name: str, fn):
        self.plugins.register(hook_name, fn)

    def _persistAtomically(self, path, data_bytes: bytes):
        dirn = os.path.dirname(path)
        fd, tmp = tempfile.mkstemp(dir=dirn)
        os.write(fd, data_bytes)
        os.close(fd)
        os.replace(tmp, path)

    def batchUpsert(self, records: list):
        self.lock.acquire()
        try:
            # pre-upsert plugins
            self.plugins.run("pre_upsert", records)
            # validate all
            for rec in records:
                enforce_schema(rec)
            # apply ttl filter: none here
            # persist all first to temp storage
            paths = []
            for rec in records:
                aid = rec["auditID"]
                rec = {**rec}
                rec.setdefault("status", "active")
                pt = json.dumps(rec).encode()
                ct = self.encr.encrypt(pt)
                path = os.path.join(self.data_dir, f"{aid}.enc")
                self._persistAtomically(path, ct)
                paths.append((aid, rec, path))
            # commit in-memory
            for aid, rec, path in paths:
                self.records[aid] = {"record": rec, "path": path}
            self._rebuild_indexes()
            # post-upsert plugins
            self.plugins.run("post_upsert", records)
        finally:
            self.lock.release()

    def _match_query(self, record, query: dict):
        for k, v in query.items():
            if record.get(k) != v:
                return False
        return True

    def delete(self, query: dict, role: str):
        if role != "admin":
            raise PermissionError("delete requires admin role")
        to_delete = [aid for aid, info in self.records.items() if self._match_query(info["record"], query)]
        self.plugins.run("pre_delete", to_delete)
        for aid in to_delete:
            path = self.records[aid]["path"]
            os.remove(path)
            del self.records[aid]
        self._rebuild_indexes()
        self.plugins.run("post_delete", to_delete)

    def softDelete(self, query: dict, role: str):
        if role not in ("admin", "auditor"):
            raise PermissionError("softDelete requires admin or auditor role")
        to_archive = [info for aid, info in self.records.items() if self._match_query(info["record"], query)]
        self.plugins.run("pre_soft_delete", to_archive)
        for info in to_archive:
            rec = info["record"]
            rec["status"] = "archived"
            pt = json.dumps(rec).encode()
            ct = self.encr.encrypt(pt)
            path = info["path"]
            self._persistAtomically(path, ct)
        self._rebuild_indexes()
        self.plugins.run("post_soft_delete", to_archive)

    def query(self, query: dict):
        now = datetime.utcnow()
        expired = []
        # TTL enforcement
        for aid, info in list(self.records.items()):
            ts = datetime.fromisoformat(info["record"]["timestamp"])
            if now - ts > timedelta(days=self.ttl_days):
                expired.append(aid)
        for aid in expired:
            path = self.records[aid]["path"]
            os.remove(path)
            del self.records[aid]
        if expired:
            self._rebuild_indexes()
        # apply query
        results = []
        for info in self.records.values():
            rec = info["record"]
            if self._match_query(rec, query):
                results.append(rec.copy())
        return results

    def startRestServer(self, host="127.0.0.1", port=5000):
        from .server import create_app
        app = create_app(self)
        app.run(host=host, port=port)
