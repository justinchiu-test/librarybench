import asyncio
import inspect

def pytest_configure(config):
    # Register the asyncio marker to avoid "unknown marker" warnings.
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")

def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine, run it on the event loop,
    but only pass in the fixtures that the function actually declares.
    """
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Only pass the fixtures that the test function actually has parameters for
        sig = inspect.signature(pyfuncitem.obj)
        filtered_args = {
            name: value
            for name, value in pyfuncitem.funcargs.items()
            if name in sig.parameters
        }
        loop.run_until_complete(pyfuncitem.obj(**filtered_args))
        return True
    # For non-async tests, let pytest handle them normally.
