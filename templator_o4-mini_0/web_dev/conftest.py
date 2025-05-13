import pytest
import inspect
import asyncio

def pytest_configure(config):
    # Register the 'asyncio' marker so pytest doesn't warn it's unknown.
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to be run as an asyncio coroutine"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test is marked with @pytest.mark.asyncio and is a coroutine function,
    run it to completion on a new event loop and tell pytest we've handled it.
    """
    if pyfuncitem.get_closest_marker("asyncio"):
        testfunc = pyfuncitem.obj
        if inspect.iscoroutinefunction(testfunc):
            # create and use a fresh loop (avoiding DeprecationWarning for get_event_loop)
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(testfunc(**pyfuncitem.funcargs))
            finally:
                loop.close()
                asyncio.set_event_loop(None)
            return True
    # otherwise, fall back to the normal pytest runner
