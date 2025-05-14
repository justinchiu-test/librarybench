import asyncio
import pytest
import inspect

@pytest.fixture
def event_loop():
    """
    Provide a fresh event loop for each test that needs one.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def pytest_pyfunc_call(pyfuncitem):
    """
    A minimal hook to run async def test functions without requiring pytest-asyncio.
    """
    test_func = pyfuncitem.obj
    if asyncio.iscoroutinefunction(test_func):
        # Select only those funcargs that match the test function signature
        sig = inspect.signature(test_func)
        call_kwargs = {
            name: value
            for name, value in pyfuncitem.funcargs.items()
            if name in sig.parameters
        }

        # Use the provided event_loop fixture if available, else create one
        loop = pyfuncitem.funcargs.get('event_loop') or asyncio.new_event_loop()
        try:
            loop.run_until_complete(test_func(**call_kwargs))
        finally:
            # Close newly created loop if we didn't get it from the fixture
            if 'event_loop' not in pyfuncitem.funcargs:
                loop.close()
        return True
    # Let pytest handle non-async tests normally
