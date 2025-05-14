import asyncio
import inspect
import pytest

def pytest_configure(config):
    # register the asyncio marker
    config.addinivalue_line(
        "markers", "asyncio: mark test as async to be run with an event loop"
    )

@pytest.fixture
def event_loop():
    """
    Provide a fresh event loop for each test marked with asyncio.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def pytest_pyfunc_call(pyfuncitem):
    """
    Hook to run async tests marked with @pytest.mark.asyncio.
    """
    if "asyncio" in pyfuncitem.keywords:
        # get the event loop fixture
        loop = pyfuncitem.funcargs.get("event_loop")
        if loop is None:
            loop = asyncio.new_event_loop()
        # filter out fixtures not in function signature
        sig = inspect.signature(pyfuncitem.obj)
        kwargs = {
            name: value
            for name, value in pyfuncitem.funcargs.items()
            if name in sig.parameters
        }
        # run the test coroutine
        loop.run_until_complete(pyfuncitem.obj(**kwargs))
        return True
    # otherwise, let pytest handle it
    return None
