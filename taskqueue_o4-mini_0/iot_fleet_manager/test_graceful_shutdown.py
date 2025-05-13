import threading
import time
import pytest
from iot.graceful_shutdown import GracefulShutdownManager

def test_shutdown_without_tasks():
    gsm = GracefulShutdownManager()
    assert gsm.shutdown(timeout=0.1)

def test_shutdown_with_inflight():
    gsm = GracefulShutdownManager()
    gsm.start_task()
    def end_task():
        time.sleep(0.1)
        gsm.end_task()
    threading.Thread(target=end_task).start()
    result = gsm.shutdown(timeout=1)
    assert result

def test_start_after_shutdown():
    gsm = GracefulShutdownManager()
    gsm.shutdown(timeout=0)
    with pytest.raises(RuntimeError):
        gsm.start_task()
