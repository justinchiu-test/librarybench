import asyncio
import inspect
import pytest

def pytest_configure(config):
    # register the asyncio marker to avoid unknown‐marker warnings
    config.addinivalue_line("markers", "asyncio: mark async tests to be run with an event loop")

def pytest_pyfunc_call(pyfuncitem):
    """
    Hook to allow pytest to run async test functions without requiring pytest-asyncio.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Create a fresh event loop for each test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async test function
            loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # Return True to signal that we've handled this test call
        return True
    # For non-async tests, do nothing special (pytest will handle them)
