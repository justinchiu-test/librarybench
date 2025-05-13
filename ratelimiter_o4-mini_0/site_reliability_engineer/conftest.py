import asyncio
import inspect
import pytest

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine (async def), run it on an asyncio event loop
    so that @pytest.mark.asyncio tests will actually execute even without pytest-asyncio.
    """
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        # get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # run the coroutine test
        loop.run_until_complete(testfunction(**pyfuncitem.funcargs))
        return True  # we've handled the call

    # else let pytest handle non-async tests
    return None
