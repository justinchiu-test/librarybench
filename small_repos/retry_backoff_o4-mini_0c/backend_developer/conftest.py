import asyncio
import inspect

def pytest_configure(config):
    # Register the asyncio marker to avoid "Unknown pytest.mark.asyncio" warnings.
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as asyncio (handled by custom pytest_pyfunc_call)"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    Run async test functions on an event loop when no pytest-asyncio plugin is present.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Create a fresh event loop for each test function
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            # Gather fixture arguments
            kwargs = pyfuncitem.funcargs
            # Run the coroutine
            loop.run_until_complete(test_func(**kwargs))
        finally:
            loop.close()
        # Returning True tells pytest we've handled the call
        return True
    # Returning None falls back to the default pytest behavior
