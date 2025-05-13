import pytest
from retry_framework.cancellation import CancellationPolicy

def test_cancellation_policy():
    cp = CancellationPolicy()
    assert not cp.is_cancelled()
    cp.cancel()
    assert cp.is_cancelled()
