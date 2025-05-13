import pytest
import threading
from retry_toolkit.cancellation_policy import CancellationPolicy

def test_cancel_and_check():
    policy = CancellationPolicy()
    assert not policy.is_cancelled()
    policy.cancel()
    assert policy.is_cancelled()
    with pytest.raises(Exception):
        policy.check_cancelled()

def test_thread_safe():
    policy = CancellationPolicy()
    def worker():
        policy.cancel()
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    assert policy.is_cancelled()
