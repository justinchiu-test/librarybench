import asyncio
import inspect

def pytest_configure(config):
    # Register the asyncio marker so there is no "unknown marker" warning.
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it in a new event loop.
    This lets pytest run `async def` tests without pytest-asyncio.
    """
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            # funcargs holds any fixtures
            loop.run_until_complete(testfunc(**pyfuncitem.funcargs))
        finally:
            loop.close()
        # we handled the call ourselves, skip the default runner
        return True
    # else let pytest handle it normally
