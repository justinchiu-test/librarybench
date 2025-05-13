import pytest
import asyncio
import inspect

def pytest_configure(config):
    # register the asyncio marker to silence warnings
    config.addinivalue_line(
        "markers", "asyncio: mark test to be run with asyncio event loop"
    )

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it in a new event loop.
    Return True to indicate we've handled the call.
    """
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        loop = asyncio.new_event_loop()
        try:
            # run the async test, passing in any fixtures
            loop.run_until_complete(testfunc(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True
    # otherwise let pytest handle it normally
