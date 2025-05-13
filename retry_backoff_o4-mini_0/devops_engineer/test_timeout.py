import time
import pytest
from retry_framework.timeout import timeout_per_attempt

@timeout_per_attempt(0.1)
def slow():
    time.sleep(0.2)
    return 'done'

def test_timeout_per_attempt():
    with pytest.raises(TimeoutError):
        slow()
