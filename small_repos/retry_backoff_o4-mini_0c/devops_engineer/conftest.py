import inspect
import asyncio
import pytest

def pytest_configure(config):
    # Register the asyncio marker so pytest won’t warn about it
    config.addinivalue_line(
        "markers", "asyncio: mark test to run under asyncio event loop"
    )

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is marked with @pytest.mark.asyncio and is an async def,
    run it to completion with asyncio rather than using pytest's normal call.
    """
    if "asyncio" in pyfuncitem.keywords:
        test_func = pyfuncitem.obj
        if inspect.iscoroutinefunction(test_func):
            # Gather fixture arguments
            funcargs = pyfuncitem.funcargs
            # Run the coroutine under the default event loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(test_func(**funcargs))
            return True  # Skip the normal pytest call path
    # else let pytest handle it normally
