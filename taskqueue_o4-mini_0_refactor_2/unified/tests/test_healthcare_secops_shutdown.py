import pytest
from healthcare_secops.pipeline.shutdown import GracefulShutdown

def test_graceful_shutdown():
    gs = GracefulShutdown()
    finish = gs.start_task()
    finish()
    gs.shutdown(timeout=1)

def test_shutdown_timeout():
    gs = GracefulShutdown()
    finish = gs.start_task()
    with pytest.raises(TimeoutError):
        gs.shutdown(timeout=0.01)
    finish()
