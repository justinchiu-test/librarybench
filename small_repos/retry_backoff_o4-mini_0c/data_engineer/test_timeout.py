import pytest
import time
from retry_toolkit.timeout import timeout_per_attempt

def test_timeout_within():
    with timeout_per_attempt(1):
        time.sleep(0.1)

def test_timeout_exceed():
    with pytest.raises(TimeoutError):
        with timeout_per_attempt(0.1):
            time.sleep(0.2)
