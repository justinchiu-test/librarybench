from sre.task_queue.audit import AuditLog

def test_audit_logging():
    a = AuditLog()
    a.log('evt1', {'x':1})
    a.log('evt2', {'y':2})
    all_events = a.get_events()
    assert len(all_events) == 2
    evt1 = a.get_events('evt1')
    assert len(evt1) == 1
    assert evt1[0][1] == 'evt1'
