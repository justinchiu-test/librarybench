import pytest
from background_dispatcher import Dispatcher, SimpleBackend

def test_register_and_use_backend():
    dsp = Dispatcher()
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('simple', backend)
    assert 'simple' in dsp.backends
    dsp.use_backend('simple')
    assert dsp.default_backend is backend

def test_enqueue_and_query_and_cancel_and_bump():
    dsp = Dispatcher()
    dsp.set_role('alice', 'user')
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('b', backend)
    dsp.use_backend('b')
    task_id = dsp.api_enqueue_image_task('alice', {'format': 'none'})
    assert isinstance(task_id, int)
    status = dsp.api_query_progress('alice', task_id)
    assert status in ('completed', 'failed')
    # Cancel should fail as it's already run
    assert not dsp.api_cancel_task('alice', task_id)
    # Bump priority
    assert dsp.api_bump_priority('alice', task_id, 5)
    assert dsp.tasks[task_id]['priority'] == 5

def test_set_queue_limits():
    dsp = Dispatcher()
    dsp.set_queue_limits('queue1', 10)
    assert dsp.queue_limits['queue1'] == 10
