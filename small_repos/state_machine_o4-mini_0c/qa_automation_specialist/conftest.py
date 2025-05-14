import pytest
import asyncio
import inspect

def pytest_configure(config):
    # Register the asyncio marker so we don't get "unknown marker" warnings
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test (mapped to anyio)"
    )
    # Ensure there's a default event loop for all tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def pytest_collection_modifyitems(config, items):
    # For every test marked with @pytest.mark.asyncio, also mark it as anyio
    for item in items:
        if item.get_closest_marker("asyncio"):
            item.add_marker(pytest.mark.anyio)

def pytest_pyfunc_call(pyfuncitem):
    """
    Execute async test functions by running them in the default event loop.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Prepare function arguments (fixtures)
        funcargs = pyfuncitem.funcargs
        # Run the coroutine in the existing event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_func(**funcargs))
        # Indicate that we've handled the call
        return True
    # For non-async functions, let pytest handle them normally
