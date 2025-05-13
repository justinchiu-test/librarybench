import pytest
import inspect
import asyncio

def pytest_configure(config):
    # Register the "asyncio" marker to avoid UnknownMarkWarning
    config.addinivalue_line(
        "markers", "asyncio: mark test as async using asyncio"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    Execute async test functions by running them in a new event loop.
    This allows async def tests (marked with @pytest.mark.asyncio) to run
    without requiring pytest-asyncio.
    """
    test_fn = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_fn):
        # Create a fresh event loop for each test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the coroutine
            loop.run_until_complete(test_fn(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # Returning True prevents pytest from executing the function again
        return True

def pytest_collection_modifyitems(config, items):
    """
    Remap @pytest.mark.asyncio to @pytest.mark.anyio so that the async
    tests (marked with asyncio) will also be marked anyio (if anyio plugin is present).
    """
    for item in items:
        if any(marker.name == "asyncio" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.anyio)
