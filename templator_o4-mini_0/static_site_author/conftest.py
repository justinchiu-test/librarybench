import inspect
import asyncio

def pytest_pyfunc_call(pyfuncitem):
    """
    pytest hook to run async test functions under asyncio.run
    when no pytest-asyncio (or similar) plugin is installed.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Run the coroutine and mark it as handled
        asyncio.run(test_func(**pyfuncitem.funcargs))
        return True
    # For non-async tests, let pytest handle them normally
