import time
from clinical_researcher.form_system.audit import AuditLog

def test_audit_log_records():
    log = AuditLog()
    log.record('f1', None, 'v1')
    time.sleep(0.01)
    log.record('f1', 'v1', 'v2')
    hist = log.get_history()
    assert len(hist) == 2
    assert hist[0]['field'] == 'f1'
    assert hist[0]['old'] is None
    assert hist[1]['new'] == 'v2'
    # timestamps increasing
    assert hist[1]['timestamp'] >= hist[0]['timestamp']
