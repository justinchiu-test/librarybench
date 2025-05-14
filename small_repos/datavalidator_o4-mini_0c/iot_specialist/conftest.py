import asyncio
import inspect
import pytest

def pytest_configure(config):
    # Register the asyncio marker to suppress “unknown mark” warnings
    config.addinivalue_line("markers", "asyncio: mark test as asyncio coroutine")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test item is an async def (a coroutine function), run it on
    a fresh event loop instead of skipping it.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        # Returning True tells pytest we’ve handled the call
        return True
