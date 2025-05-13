import time
import pytest
from scheduler import Scheduler, InlineExecutor

class DummyBackend:
    def __init__(self):
        self.saved = []
    def save(self, task_name, result, status):
        self.saved.append((task_name, result, status))

class DummyExecutor:
    def __init__(self):
        self.calls = []
    def run(self, func, *args, **kwargs):
        self.calls.append((func, args, kwargs))
        return func(*args, **kwargs)

def test_add_storage_backend_and_save():
    sched = Scheduler()
    backend = DummyBackend()
    sched.add_storage_backend(backend)
    # register and run task
    sched.register_task('t1', lambda: 'ok')
    result = sched.run_task('t1')
    assert result == 'ok'
    assert backend.saved == [('t1', 'ok', 'success')]

def test_set_executor():
    sched = Scheduler()
    executor = DummyExecutor()
    sched.set_executor(executor)
    # register and run
    sched.register_task('t2', lambda x: x + 1)
    result = sched.run_task('t2', 5)
    assert result == 6
    assert len(executor.calls) == 1
    func, args, kwargs = executor.calls[0]
    assert func(3) == 3

def test_pre_post_hooks_execution_order():
    sched = Scheduler()
    order = []
    def pre(name, *args, **kwargs):
        order.append(('pre', name))
    def post(name, result, status):
        order.append(('post', name, status))
    sched.on_pre_execute(pre)
    sched.on_post_execute(post)
    sched.register_task('t3', lambda: 'done')
    sched.run_task('t3')
    assert order == [('pre', 't3'), ('post', 't3', 'success')]

def test_dependencies():
    sched = Scheduler()
    order = []
    sched.register_task('a', lambda: order.append('a'))
    sched.register_task('b', lambda: order.append('b'))
    sched.add_dependency('b', 'a')
    sched.run_task('b')
    assert order == ['a', 'b']

def test_create_api_endpoint_and_call():
    sched = Scheduler()
    sched.create_api_endpoint('run', lambda x: x * 2)
    assert 'run' in sched.endpoints
    assert sched.endpoints['run'](4) == 8

def test_graceful_shutdown_blocks_new_tasks():
    sched = Scheduler()
    sched.register_task('t', lambda: None)
    sched.graceful_shutdown()
    with pytest.raises(RuntimeError):
        sched.run_task('t')

def test_send_alert():
    sched = Scheduler()
    sched.send_alert('slack', 'Test failed')
    assert sched.alerts == [{'channel': 'slack', 'message': 'Test failed'}]

def test_throttle_task():
    sched = Scheduler()
    sched.throttle_task('t', 1)
    sched.register_task('t', lambda: 'ok')
    first = sched.run_task('t')
    second = sched.run_task('t')
    assert first == 'ok'
    assert second is None
    time.sleep(1.1)
    third = sched.run_task('t')
    assert third == 'ok'

def test_register_lifecycle_hooks_and_run():
    sched = Scheduler()
    calls = {'startup': 0, 'shutdown': 0}
    def su():
        calls['startup'] += 1
    def sd():
        calls['shutdown'] += 1
    sched.register_lifecycle_hook('startup', su)
    sched.register_lifecycle_hook('shutdown', sd)
    sched.run_lifecycle_hooks('startup')
    sched.run_lifecycle_hooks('shutdown')
    assert calls['startup'] == 1
    assert calls['shutdown'] == 1
    with pytest.raises(ValueError):
        sched.register_lifecycle_hook('invalid', lambda: None)

def test_catch_up_missed_runs():
    sched = Scheduler()
    # Task that fails first, succeeds next
    class Task:
        def __init__(self):
            self.count = 0
        def __call__(self):
            self.count += 1
            if self.count == 1:
                raise ValueError("fail")
            return 'ok'
    t = Task()
    sched.register_task('t', t)
    # first run fails
    res1 = sched.run_task('t')
    assert isinstance(res1, Exception)
    assert len(sched.missed_runs) == 1
    # now catch up
    sched.catch_up_missed_runs()
    assert len(sched.missed_runs) == 0
    # check history: one failure, one success
    statuses = [h['status'] for h in sched.task_history if h['task_name']=='t']
    assert statuses == ['failure', 'success']

def test_run_task_missing():
    sched = Scheduler()
    with pytest.raises(KeyError):
        sched.run_task('not_exists')

def test_task_history_records():
    sched = Scheduler()
    sched.register_task('x', lambda: 123)
    sched.run_task('x')
    history = sched.task_history
    assert history[-1]['task_name'] == 'x'
    assert history[-1]['result'] == 123
    assert history[-1]['status'] == 'success'
