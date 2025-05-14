import datetime
import hashlib
import json

class AuditLogger:
    def __init__(self):
        self.logs = []
        self._last_hash = ""

    def log(self, tenant_id, action, details):
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "tenant_id": tenant_id,
            "action": action,
            "details": details,
            "prev_hash": self._last_hash
        }
        entry_str = json.dumps(entry, sort_keys=True).encode('utf-8')
        current_hash = hashlib.sha256(entry_str).hexdigest()
        entry["hash"] = current_hash
        self._last_hash = current_hash
        self.logs.append(entry)

    def get_logs(self):
        return list(self.logs)
