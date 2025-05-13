import pytest
import time
from event_system import (
    subscribe, subscribe_once, unsubscribe, set_global_error_handler,
    on_error, dead_letter_queue, add_filter, publish, publish_delayed,
    run_delayed, with_transaction, attach_logger, context_middleware,
    set_context, _dlqs
)

def test_subscribe_and_publish():
    results = []
    def handler(e):
        results.append(('h', e['msg']))
    h = subscribe(handler)
    publish({'msg': 'test1'})
    assert results == [('h', 'test1')]
    unsubscribe(h)

def test_subscribe_once():
    results = []
    def handler(e):
        results.append(('o', e.get('session')))
    h = subscribe_once(handler)
    publish({'msg':'one','session':'S1'})
    publish({'msg':'two','session':'S1'})
    publish({'msg':'three','session':'S2'})
    assert results == [('o','S1'), ('o','S2')]
    unsubscribe(h)

def test_unsubscribe():
    results = []
    def handler(e):
        results.append(1)
    h = subscribe(handler)
    unsubscribe(h)
    publish({'msg':'x'})
    assert results == []

def test_global_error_handler():
    errors = []
    def global_err(e, ev): errors.append(('g', str(e)))
    set_global_error_handler(global_err)
    def bad(e): raise RuntimeError("fail")
    h = subscribe(bad)
    publish({'msg':'err'})
    assert errors and errors[0][0] == 'g'
    unsubscribe(h)

def test_on_error():
    errors = []
    def bad(e): raise ValueError("badpy")
    def cb(err, ev): errors.append(('cb', type(err).__name__, ev))
    on_error(bad, cb)
    h = subscribe(bad)
    publish({'msg':'x'})
    assert errors and errors[0][0] == 'cb'
    unsubscribe(h)

def test_dead_letter_queue_and_filter():
    dlq_name = dead_letter_queue("security_dlq")
    add_filter(lambda e: not e.get('auth'))
    # unauthenticated
    publish({'msg':'u1','auth':False})
    assert _dlqs[dlq_name] and _dlqs[dlq_name][-1]['msg'] == 'u1'
    # authenticated
    called = []
    def ok(e): called.append(e['msg'])
    h = subscribe(ok)
    publish({'msg':'u2','auth':True})
    assert called == ['u2']
    unsubscribe(h)

def test_publish_delayed():
    results = []
    def h(e): results.append(e['msg'])
    subscribe(h)
    publish_delayed({'msg':'d1'}, 0.1)
    assert results == []
    run_delayed()
    assert results == ['d1']

def test_with_transaction_success():
    results = []
    def h(e): results.append(e['msg'])
    subscribe(h)
    with with_transaction():
        publish({'msg':'t1'})
        publish({'msg':'t2'})
    assert results == ['t1', 't2']

def test_with_transaction_failure():
    results = []
    def h(e): results.append(e['msg'])
    subscribe(h)
    with pytest.raises(Exception):
        with with_transaction():
            publish({'msg':'fail1'})
            raise Exception("oops")
            publish({'msg':'fail2'})
    assert results == []

def test_attach_logger():
    logs = []
    def logger(msg): logs.append(msg)
    attach_logger(logger)
    # actions
    def h(e): pass
    subscribe(h)
    publish({'msg':'log1'})
    publish_delayed({'msg':'log2'}, 0)
    run_delayed()
    assert any("subscribe: handler=h" in l for l in logs)
    assert any("publish: delivering to h" in l for l in logs)
    assert any("publish_delayed: scheduled" in l for l in logs)
    assert any("run_delayed: executed" in l for l in logs)

def test_context_middleware():
    results = []
    def h(e):
        results.append(e.get('context'))
    wrapped = context_middleware()(h)
    subscribe(wrapped)
    ctx = {'user_id':'U1','ip':'127.0.0.1','session':'S'}
    set_context(ctx)
    publish({'msg':'c1'})
    assert results == [ctx]
