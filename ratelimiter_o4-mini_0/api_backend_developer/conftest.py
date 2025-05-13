import asyncio
import inspect
import pytest
from _pytest.python import Function

def pytest_configure(config):
    # register the asyncio marker to silence warnings
    config.addinivalue_line(
        "markers", "asyncio: mark test to be run with asyncio event loop"
    )

def pytest_pycollect_makeitem(collector, name, obj):
    # collect async def functions as test items
    if inspect.iscoroutinefunction(obj):
        return Function.from_parent(collector, name=name, callobj=obj)
    return None

def pytest_pyfunc_call(pyfuncitem):
    # handle tests marked with @pytest.mark.asyncio
    if "asyncio" in pyfuncitem.keywords:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # indicate that we've handled the call
        return True
    # let pytest handle non-async tests
    return None
