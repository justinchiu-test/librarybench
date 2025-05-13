import asyncio
import inspect
import pytest

def pytest_pycollect_makeitem(collector, name, obj):
    """
    Collect async def test functions as normal pytest.Function items
    so they aren't skipped when no external asyncio plugin is installed.
    """
    if name.startswith("test") and inspect.iscoroutinefunction(obj):
        # Build a standard pytest Function from this collector
        # so that pytest will attempt to run it later.
        return pytest.Function.from_parent(collector, name=name)
    # For all others, let pytest proceed normally
    return None

def pytest_pyfunc_call(pyfuncitem):
    """
    Run async test functions by scheduling them on a fresh asyncio loop,
    allowing @pytest.mark.asyncio or bare async def tests to execute.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        loop = asyncio.new_event_loop()
        try:
            # get any fixture args or an empty dict
            kwargs = getattr(pyfuncitem, "funcargs", {})
            loop.run_until_complete(test_func(**kwargs))
            # signal that we've executed the test ourselves
            return True
        finally:
            loop.close()
    # return None so pytest does its normal thing for sync tests
    return None
