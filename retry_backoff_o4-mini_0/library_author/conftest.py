import asyncio
import inspect
import pytest

def pytest_configure(config):
    # register the asyncio marker to avoid unknown‐mark warnings
    config.addinivalue_line(
        "markers", "asyncio: mark test as asyncio (runs under an event loop)"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it in the event loop.
    Otherwise, let pytest handle it normally.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # get (or create) an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # run the coroutine, injecting any fixtures
        loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        return True  # we've handled the call
    # returning None lets pytest continue with the normal call path
    return None
