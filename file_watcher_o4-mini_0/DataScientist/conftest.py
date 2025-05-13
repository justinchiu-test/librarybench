import inspect
import asyncio
import pytest

def pytest_configure(config):
    # register the asyncio marker so pytest won't warn about it
    config.addinivalue_line(
        "markers", "asyncio: mark async tests to run in an event loop"
    )

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    Override pytest behavior for async tests if no asyncio plugin is installed.
    Run coroutine tests in a fresh event loop, but only pass the parameters
    that the test function actually declares.
    """
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            sig = inspect.signature(pyfuncitem.obj)
            # filter out any fixture args the test function doesn't accept
            filtered = {
                name: pyfuncitem.funcargs[name]
                for name in sig.parameters
                if name in pyfuncitem.funcargs
            }
            loop.run_until_complete(pyfuncitem.obj(**filtered))
        finally:
            loop.close()
        return True
