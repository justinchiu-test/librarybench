import pytest

@pytest.fixture
def anyio_backend():
    # Force AnyIO to use the asyncio backend for all @pytest.mark.anyio tests
    return "asyncio"
