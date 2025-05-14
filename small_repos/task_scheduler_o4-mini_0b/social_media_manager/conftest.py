import asyncio
import inspect

def pytest_configure(config):
    # Register the 'asyncio' marker to avoid unknown‐marker warnings
    config.addinivalue_line(
        "markers", "asyncio: mark the test as an asyncio (alias to anyio) test"
    )

def pytest_collection_modifyitems(config, items):
    # Any test marked with @pytest.mark.asyncio should also be marked anyio,
    # so that the AnyIO plugin will actually run it rather than skip it.
    for item in items:
        if item.get_closest_marker("asyncio"):
            item.add_marker("anyio")

def pytest_pyfunc_call(pyfuncitem):
    """
    Hook to allow running async test functions even without pytest-asyncio.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Run the async test function in a fresh event loop
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # Returning True tells pytest we've handled the call
        return True
