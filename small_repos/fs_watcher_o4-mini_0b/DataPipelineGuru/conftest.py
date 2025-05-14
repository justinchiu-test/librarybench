import asyncio
import inspect
import pytest
from _pytest.config import hookimpl

def pytest_configure(config):
    # Register the asyncio marker to silence the "unknown mark" warning
    config.addinivalue_line(
        "markers", "asyncio: mark test to be run with asyncio event loop"
    )

@hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """
    Collect async def test functions as pytest.Function items so
    that pytest_runtest_call can handle them instead of skipping.
    """
    if inspect.iscoroutinefunction(obj):
        return pytest.Function.from_parent(collector, name=name)

@hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it in the current event loop.
    Returning True tells pytest we've handled the call.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Ensure we have an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Only pass fixtures that match the test function's signature
        sig = inspect.signature(test_func)
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in sig.parameters.keys()
            if name in pyfuncitem.funcargs
        }
        loop.run_until_complete(test_func(**kwargs))
        return True
