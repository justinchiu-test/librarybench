import pytest
import time

from iot_scheduler import (
    Scheduler,
    SQLiteStorageBackend,
    RedisStorageBackend,
    AsyncioExecutor,
    ThreadExecutor
)

def test_storage_backends():
    sch = Scheduler()
    sq = SQLiteStorageBackend()
    rd = RedisStorageBackend()
    sch.add_storage_backend('sql', sq)
    sch.add_storage_backend('redis', rd)
    assert sch.storage_backends['sql'] is sq
    assert sch.storage_backends['redis'] is rd
    sq.save('k1', 'v1')
    assert sq.load('k1') == 'v1'
    rd.save('k2', 'v2')
    assert rd.load('k2') == 'v2'

def test_executors_and_run_task():
    sch = Scheduler()
    ae = AsyncioExecutor()
    te = ThreadExecutor()
    sch.set_executor('async', ae)
    sch.set_executor('thread', te)
    results = {}
    def task1():
        results['t1'] = 'done1'
        return 'r1'
    def task2():
        results['t2'] = 'done2'
        return 'r2'
    sch.add_task('t1', task1, executor='async')
    sch.add_task('t2', task2, executor='thread')
    # Dependencies
    sch.add_dependency('t2', 't1')
    # Pre/Post hooks
    order = []
    @sch.on_pre_execute
    def pre(name):
        order.append(f"pre-{name}")
    @sch.on_post_execute
    def post(name, res):
        order.append(f"post-{name}-{res}")
    r1 = sch.run_task('t1')
    assert r1 == 'r1'
    # t2 depends on t1
    r2 = sch.run_task('t2')
    assert r2 == 'r2'
    # Check hooks order
    assert order[0] == 'pre-t1'
    assert order[1] == 'post-t1-r1'
    assert order[2] == 'pre-t2'
    assert order[3] == 'post-t2-r2'

def test_api_endpoints():
    sch = Scheduler()
    def handler():
        return "ok"
    sch.create_api_endpoint('/health', handler, methods=['GET'])
    assert '/health' in sch.api_endpoints
    ep = sch.api_endpoints['/health']
    assert ep['handler']() == "ok"
    assert ep['methods'] == ['GET']

def test_alerts():
    sch = Scheduler()
    sch.send_alert("critical")
    sch.send_alert("warning")
    assert sch.alerts == ["critical", "warning"]

def test_throttle_and_catch_up():
    sch = Scheduler()
    calls = []
    @sch.throttle_task(calls_per_sec=2)
    def poll(x):
        calls.append(x)
    # call 5 times quickly
    for i in range(5):
        poll(i)
    # only first two should run
    assert calls == [0,1]
    # missed should be 3 runs
    assert len(sch.missed_runs) == 3
    # catch up
    sch.catch_up_missed_runs()
    # now calls contain all
    assert calls == [0,1,2,3,4]
    assert sch.missed_runs == []

def test_lifecycle_and_shutdown():
    sch = Scheduler()
    state = {'startup': False, 'shutdown': False}
    @sch.register_lifecycle_hook('startup')
    def on_start():
        state['startup'] = True
    @sch.register_lifecycle_hook('shutdown')
    def on_stop():
        state['shutdown'] = True
    # simulate start
    for hook in sch.lifecycle_hooks['startup']:
        hook()
    assert state['startup']
    # shutdown
    sch.graceful_shutdown()
    assert not sch.running
    assert state['shutdown']

def test_graceful_sigint(monkeypatch):
    sch = Scheduler()
    state = {'shutdown': False}
    @sch.register_lifecycle_hook('shutdown')
    def on_stop():
        state['shutdown'] = True
    # simulate SIGINT
    sch._handle_sigint(None, None)
    assert not sch.running
    assert state['shutdown']
