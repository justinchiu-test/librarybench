import pytest

def pytest_configure(config):
    # Let pytest know about the "asyncio" marker (to avoid unknown‐marker warnings)
    config.addinivalue_line(
        "markers",
        "asyncio: mark test for asyncio (alias to anyio)"
    )
    # Alias pytest.mark.asyncio → pytest.mark.anyio
    # so that async tests marked with @pytest.mark.asyncio will
    # actually be treated as @pytest.mark.anyio by AnyIO.
    pytest.mark.asyncio = pytest.mark.anyio

# Override AnyIO's default backends to ONLY run under asyncio
# This fixture will replace the plugin's anyio_backend fixture,
# so we no longer try to spin up trio (which isn't installed).
@pytest.fixture(name="anyio_backend", params=[("asyncio", {})], ids=lambda x: x[0])
def _anyio_backend(request):
    return request.param
