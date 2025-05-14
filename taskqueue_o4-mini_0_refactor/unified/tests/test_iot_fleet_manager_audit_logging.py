import os
import tempfile
from iot_fleet_manager.iot.audit_logging import AuditLogger

def test_log_and_read():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
        logger = AuditLogger(path)
        logger.log('test_event', {'key': 'value'})
        logs = logger.read_logs()
        assert len(logs) == 1
        entry = logs[0]
        assert entry['event_type'] == 'test_event'
        assert entry['details']['key'] == 'value'
    finally:
        os.remove(path)
