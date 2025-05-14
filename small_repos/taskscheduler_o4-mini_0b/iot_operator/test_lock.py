from iot_scheduler.lock import acquire_distributed_lock

def test_lock_context_manager():
    with acquire_distributed_lock('test'):
        # Inside lock, should execute without error
        x = 1
    assert x == 1
