import pytest
import signal
from scheduler.scheduler import Scheduler
from scheduler.backends import RedisBackend, PostgresBackend
from scheduler.executors import MultiprocessingExecutor, AsyncioExecutor

def test_storage_backends():
    sched = Scheduler()
    r = RedisBackend(host='127.0.0.1', port=6380)
    p = PostgresBackend(dsn='dbname=test')
    sched.add_storage_backend('redis', r)
    sched.add_storage_backend('pgsql', p)
    assert sched.storage_backends['redis'] is r
    assert sched.storage_backends['pgsql'] is p
    assert r.connect() == 'Connected to Redis at 127.0.0.1:6380'
    assert p.connect() == 'Connected to Postgres with DSN dbname=test'

def test_set_executor_and_run_task():
    sched = Scheduler()
    executor = MultiprocessingExecutor(processes=1)
    sched.set_executor(executor)
    def sample_task(x, y):
        return x + y
    sched.task_add = sample_task
    result = sched.run('add', 2, 3)
    assert result == 5
    # test asyncio executor
    sched2 = Scheduler()
    aexec = AsyncioExecutor()
    sched2.set_executor(aexec)
    async def async_task(x):
        return x * 2
    sched2.task_double = async_task
    result2 = sched2.run('double', 4)
    assert result2 == 8

def test_pre_and_post_hooks_and_dependency_and_catchup():
    sched = Scheduler()
    executor = MultiprocessingExecutor(processes=1)
    sched.set_executor(executor)
    calls = []
    @sched.catch_up_missed_runs
    def catch():
        calls.append('catchup')
    @sched.on_pre_execute
    def pre(name, *args, **kwargs):
        calls.append(f'pre-{name}')
    @sched.on_post_execute
    def post(name, err, res):
        calls.append(f'post-{name}')
    sched.add_dependency('b', 'a')
    def task_a():
        calls.append('run-a')
        return 'A'
    def task_b():
        calls.append('run-b')
        return 'B'
    sched.task_a = task_a
    sched.task_b = task_b
    result = sched.run('b')
    assert result == 'B'
    assert calls == ['catchup', 'pre-a', 'run-a', 'post-a', 'pre-b', 'run-b', 'post-b']

def test_throttle_and_alert_and_graceful_and_lifecycle():
    sched = Scheduler()
    # throttle
    @sched.throttle_task(rate_limit=5)
    def t():
        return "ok"
    assert 't' in sched.rate_limits and sched.rate_limits['t'] == 5
    # alert
    sched.send_alert('jira', 'fail')
    assert sched.alerts == [('jira', 'fail')]
    # graceful shutdown event
    assert not sched._shutdown.is_set()
    sched.graceful_shutdown()
    assert sched._shutdown.is_set()
    # lifecycle hook on shutdown via signal
    flag = {}
    def hook():
        flag['called'] = True
    sched = Scheduler()
    sched.register_lifecycle_hook('shutdown', hook)
    # simulate SIGTERM
    sched._handle_sigterm(signal.SIGTERM, None)
    assert flag.get('called', False)

def test_missing_task_or_executor_error():
    sched = Scheduler()
    with pytest.raises(Exception) as ei:
        sched.run('nonexistent')
    assert 'Task or executor not found' in str(ei.value)
