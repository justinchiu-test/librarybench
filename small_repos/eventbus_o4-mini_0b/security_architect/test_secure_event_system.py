import threading
import pytest
import time

from secure_event_system import SecureEventSystem

def test_authenticate_and_report_health():
    ses = SecureEventSystem()
    token = {'user': 'alice', 'roles': ['user']}
    with pytest.raises(PermissionError):
        ses.reportHealth()
    ses.authenticate(token)
    with pytest.raises(PermissionError):
        ses.reportHealth()
    ses.authenticate({'user': 'admin', 'roles': ['admin']})
    health = ses.reportHealth()
    assert 'threads' in health and 'handlers' in health

def test_balance_load_thread_safe():
    ses = SecureEventSystem()
    results = []
    def task(x):
        return x * x
    def worker(i):
        results.append(ses.balanceLoad(task, i))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sorted(results) == [i*i for i in range(10)]

def test_propagate_context_sync_and_async():
    ses = SecureEventSystem()
    ses.propagateContext(a=1)
    assert ses.getContext().get('a') == 1
    def worker():
        # context is thread-local; should start empty
        assert ses.getContext() == {}
        ses.propagateContext(b=2)
        assert ses.getContext().get('b') == 2
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    # main thread context unaffected by worker
    assert ses.getContext().get('b') is None

def test_serializer_registration_and_usage():
    ses = SecureEventSystem()
    ser = lambda x: f"SER:{x}"
    deser = lambda x: x.replace("SER:", "")
    ses.registerSerializer('s1', ser, deser)
    data = ses.serialize('s1', 'data')
    assert data == "SER:data"
    assert ses.deserialize('s1', data) == 'data'
    with pytest.raises(KeyError):
        ses.serialize('unknown', {})

def test_persist_and_verify_events_with_tamper_detection():
    ses = SecureEventSystem()
    key = b'secret'
    ses.propagateContext(key=key)
    ses.persistEvents('t1', {'e': 1})
    ses.persistEvents('t1', {'e': 2})
    assert ses.verifyEvents('t1')
    # Tamper with stored signature
    ses._events['t1'][0] = (ses._events['t1'][0][0], '0')
    assert not ses.verifyEvents('t1')

def test_publish_sync_and_handler_order():
    ses = SecureEventSystem()
    calls = []
    def h1(e): calls.append(('h1', e)); return 'r1'
    def h2(e): calls.append(('h2', e)); return 'r2'
    ses.registerHandler(h1)
    ses.registerHandler(h2)
    results = ses.publishSync('evt')
    assert results == ['r1', 'r2']
    assert calls == [('h1', 'evt'), ('h2', 'evt')]

def test_update_and_get_config():
    ses = SecureEventSystem()
    ses.updateConfig(timeout=100, backpressure=True)
    cfg = ses.getConfig()
    assert cfg['timeout'] == 100
    assert cfg['backpressure'] is True

def test_register_and_get_extension():
    ses = SecureEventSystem()
    ext = object()
    ses.registerExtension('ext1', ext)
    assert ses.getExtension('ext1') is ext
    assert ses.getExtension('unknown') is None

def test_handle_errors_decorator_and_quarantine():
    ses = SecureEventSystem()
    state = {'count': 0}
    def faulty(e):
        state['count'] += 1
        raise RuntimeError("fail")
    wrapped = ses.handleErrors(faulty)
    result = wrapped('event1')
    assert result is None
    # Should have retried 3 times and quarantined
    assert state['count'] == 3
    assert ses.getQuarantine() == ['event1']
    logs = ses.getLogs()
    assert any("fail" in msg for msg in logs)

def test_handle_errors_eventual_success():
    ses = SecureEventSystem()
    state = {'count': 0}
    def flaky(e):
        state['count'] += 1
        if state['count'] < 2:
            raise ValueError("temp")
        return "ok"
    wrapped = ses.handleErrors(flaky)
    result = wrapped('x')
    assert result == "ok"
    # Should not quarantine on success
    assert ses.getQuarantine() == []
    # Should have logged one error
    logs = ses.getLogs()
    assert any("temp" in msg for msg in logs)
