import pytest

# Alias the asyncio marker to anyio so that pytest.mark.asyncio actually uses anyio
pytest.mark.asyncio = pytest.mark.anyio

def pytest_configure(config):
    # Register the asyncio marker to silence unknown-mark warnings
    config.addinivalue_line("markers", "asyncio: mark test as asyncio (alias for anyio)")

# Override anyio's parametrized fixture so we always use asyncio only
@pytest.fixture
def anyio_backend(request):
    return ("asyncio", {})
