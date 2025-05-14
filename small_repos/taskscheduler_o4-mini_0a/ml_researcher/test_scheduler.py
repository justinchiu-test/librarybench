import pytest
import logging
from scheduler import (
    export_metrics,
    configure_executor,
    acquire_distributed_lock,
    dashboard_ui,
    attach_log_context,
    start_api_server,
    run_in_sandbox,
    set_job_priority,
    get_job_priority,
    register_lifecycle_hook,
    get_lifecycle_hooks,
    serialize_job,
    deserialize_job,
)

def test_export_metrics():
    exporter = export_metrics()
    assert hasattr(exporter, 'increment')
    exporter.increment('runs')
    exporter.increment('runs', 2)
    assert exporter.get('runs') == 3
    assert exporter.get('missing') == 0

def test_configure_executor_thread():
    executor = configure_executor('thread', max_workers=2)
    future = executor.submit(lambda x: x + 1, 1)
    assert future.result(timeout=1) == 2
    executor.shutdown()

def test_configure_executor_process():
    executor = configure_executor('process', max_workers=1)
    future = executor.submit(lambda x: x * 2, 3)
    assert future.result(timeout=5) == 6
    executor.shutdown()

def test_configure_executor_asyncio():
    loop = configure_executor('asyncio')
    async def add(x, y):
        return x + y
    result = loop.run_until_complete(add(2, 3))
    assert result == 5
    loop.close()

def test_configure_executor_invalid():
    with pytest.raises(ValueError):
        configure_executor('unknown')

def test_acquire_distributed_lock():
    lock1 = acquire_distributed_lock('redis://localhost', 'testlock')
    assert lock1.acquire() is True
    lock2 = acquire_distributed_lock('redis://localhost', 'testlock')
    assert lock2.acquire() is False
    assert lock1.release() is True
    assert lock2.acquire() is True
    assert lock2.release() is True

def test_dashboard_ui():
    ui = dashboard_ui()
    assert ui.start() == "Dashboard UI started"
    ui.add_route('/home', lambda: 'ok')
    assert '/home' in ui.routes
    assert callable(ui.routes['/home'])

def test_attach_log_context():
    logger = logging.getLogger('test_logger')
    context = {'experiment_id': 123, 'model': 'resnet'}
    adapter = attach_log_context(logger, **context)
    assert hasattr(adapter, 'extra')
    assert adapter.extra == context
    from logging import LoggerAdapter
    assert isinstance(adapter, LoggerAdapter)

def test_start_api_server():
    server = start_api_server('127.0.0.1', 8000)
    assert server.start() == 'API server started on 127.0.0.1:8000'
    server.add_endpoint('/run', lambda: 'running')
    assert '/run' in server.endpoints

def test_run_in_sandbox():
    proc = run_in_sandbox('cmd', ['arg1', 'arg2'], cpu_quota=50, mem_quota=128)
    assert proc.cmd == 'cmd'
    assert proc.args == ['arg1', 'arg2']
    assert proc.cpu_quota == 50
    assert proc.mem_quota == 128
    assert proc.run() == {'cmd': 'cmd', 'args': ['arg1', 'arg2']}

def test_set_job_priority():
    assert set_job_priority('job1', 10) == 10
    assert get_job_priority('job1') == 10
    assert set_job_priority('job1', 5) == 5
    assert get_job_priority('job1') == 5

def test_register_lifecycle_hook():
    def hook_func(): pass
    hooks = register_lifecycle_hook('init', hook_func)
    assert hook_func in hooks
    hooks2 = register_lifecycle_hook('init', hook_func)
    assert hooks2.count(hook_func) >= 2
    assert hook_func in get_lifecycle_hooks('init')

def test_serialize_job():
    data = {'a': 1, 'b': [2, 3]}
    b = serialize_job(data)
    assert isinstance(b, (bytes, bytearray))
    obj = deserialize_job(b)
    assert obj == data
