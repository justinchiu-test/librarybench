import pytest
import threading
from retry_toolkit.cancellation import CancellationPolicy, CancelledError

def test_cancellation_policy():
    event = threading.Event()
    policy = CancellationPolicy(event)
    # no cancel
    policy.check_cancel()
    # cancel
    event.set()
    with pytest.raises(CancelledError):
        policy.check_cancel()
