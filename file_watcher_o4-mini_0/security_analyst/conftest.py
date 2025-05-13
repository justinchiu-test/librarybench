import inspect
import asyncio

def pytest_pyfunc_call(pyfuncitem):
    """
    Run async test functions on a fresh asyncio event loop if they are defined
    as `async def`, so pytest will execute them even without pytest-asyncio.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # Return True to signal that we handled the call.
        return True
    # For non-async tests, let pytest handle them normally.
