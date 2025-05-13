import json
import os
import tempfile
from watcher.logger import AuditLogger

def test_log_event(tmp_path):
    log_file = tmp_path / "log.jsonl"
    logger = AuditLogger(str(log_file))
    event = {"action": "test", "status": "ok"}
    logger.log_event(event)
    content = log_file.read_text().strip()
    # ensure valid JSON line
    parsed = json.loads(content)
    assert parsed == event
