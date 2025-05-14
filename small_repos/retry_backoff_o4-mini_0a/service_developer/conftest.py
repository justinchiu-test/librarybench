import asyncio
import inspect

def pytest_pyfunc_call(pyfuncitem):
    """
    Pytest hook to execute async test functions even without pytest-asyncio installed.
    If the test function is a coroutine, run it with asyncio.run(), and signal that
    we've handled the call by returning True.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Run the async test in its own event loop
        asyncio.run(test_func())
        return True
    # For non-async tests, let pytest handle them normally (return None)
