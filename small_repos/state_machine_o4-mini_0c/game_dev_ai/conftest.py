import inspect
import asyncio
import pytest

def pytest_pyfunc_call(pyfuncitem):
    """
    Hook to allow async test functions (coroutines) to run
    without needing pytest-asyncio or similar plugins.
    """
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        # Obtain the event loop fixture if provided, otherwise use default
        loop = pyfuncitem.funcargs.get('event_loop') or asyncio.get_event_loop()
        # Execute the coroutine test on the loop
        loop.run_until_complete(testfunction(**pyfuncitem.funcargs))
        # Returning True tells pytest we've handled the call
        return True
    # For regular (non-async) tests, let pytest handle them normally
    return None
