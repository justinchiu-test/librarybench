import inspect
import asyncio
import pytest
from _pytest.python import Function

def pytest_pycollect_makeitem(collector, name, obj):
    """
    Collect 'async def' test functions as normal pytest.Function items,
    so they aren't skipped when no pytest-asyncio plugin is installed.
    """
    if inspect.iscoroutinefunction(obj):
        return Function.from_parent(collector, name=name, callobj=obj)

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    Execute coroutine test functions by running them on the event loop.
    """
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
        return True
