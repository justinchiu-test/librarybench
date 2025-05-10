import os
import pytest

@pytest.fixture
def tmp_env():
    """
    Temporarily clear os.environ for tests that request a clean environment.
    Restores the original environment afterwards.
    """
    old_env = os.environ.copy()
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(old_env)
