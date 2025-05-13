import inspect
import asyncio

def pytest_pyfunc_call(pyfuncitem):
    """Hook to run async test functions in their own event loop when no async plugin is present."""
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        loop = asyncio.new_event_loop()
        try:
            # Run the coroutine test function with its pytest-provided fixtures
            loop.run_until_complete(testfunction(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True
