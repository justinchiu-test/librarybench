# Enable pytest-anyio for async tests
pytest_plugins = ["anyio"]

import pytest

@pytest.fixture
def anyio_backend():
    # Force anyio to use asyncio backend only, avoid trio backend errors
    return "asyncio"

@pytest.fixture
def default_username_check():
    """
    Async fixture that simulates checking username uniqueness.
    Returns False for 'taken', True otherwise.
    """
    async def _check(username):
        return False if username == "taken" else True
    return _check
