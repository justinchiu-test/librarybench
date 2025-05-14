import asyncio
import inspect

def pytest_configure(config):
    # register the asyncio marker so pytest stops warning about it
    config.addinivalue_line(
        "markers",
        "asyncio: mark the test function as an asyncio coroutine"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it on an event loop.
    Otherwise, let pytest handle it as usual.
    """
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        # create a fresh event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Only pass in the fixtures the test actually declares
            sig = inspect.signature(testfunc)
            kwargs = {
                name: value
                for name, value in pyfuncitem.funcargs.items()
                if name in sig.parameters
            }
            loop.run_until_complete(testfunc(**kwargs))
        finally:
            loop.close()
        return True  # we've handled the call
    # else: return None so pytest continues with the default handler
