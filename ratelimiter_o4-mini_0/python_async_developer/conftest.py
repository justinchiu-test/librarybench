import inspect
import asyncio

def pytest_configure(config):
    # Register the asyncio marker so we don’t get “unknown mark” warnings
    config.addinivalue_line(
        "markers", "asyncio: mark async tests to be run under the asyncio event loop"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, drive it to completion on
    the asyncio event loop; otherwise defer to the normal runner.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Gather only the fixture arguments that the test function declares
        sig = inspect.signature(test_func)
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in sig.parameters
            if name in pyfuncitem.funcargs
        }
        # Ensure we have a usable event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Run the coroutine to completion
        loop.run_until_complete(test_func(**kwargs))
        return True
    # Non-async test, let pytest handle it
    return None
