import pytest
import inspect
import asyncio

# pick up our fixture plugin
pytest_plugins = ["ratelimiter.fixtures"]

def pytest_configure(config):
    # Tell pytest-anyio to auto‐run all async def tests
    # (so you don't need explicit @pytest.mark.anyio)
    config._inicache["anyio_mode"] = "auto"

    # Register the "asyncio" marker to suppress warnings
    config.addinivalue_line(
        "markers",
        "asyncio: alias for anyio marker to run async tests"
    )

def pytest_collection_modifyitems(config, items):
    """
    Re-tag pytest.mark.asyncio as pytest.mark.anyio
    so that the AnyIO plugin will run async coroutines
    (otherwise pytest will skip them by default).
    """
    for item in items:
        if item.get_closest_marker("asyncio"):
            item.add_marker(pytest.mark.anyio)

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is an async def, run it in the event loop
    instead of letting pytest skip it.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        return True
    # otherwise, let pytest handle it normally
