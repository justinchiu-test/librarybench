import asyncio
import pytest

def pytest_configure(config):
    # Register the asyncio marker to silence unknown‐marker warnings
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")

def pytest_pyfunc_call(pyfuncitem):
    """If the test function is an async def, run it in a fresh event loop."""
    testfunc = pyfuncitem.obj
    if asyncio.iscoroutinefunction(testfunc):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(testfunc(**pyfuncitem.funcargs))
        finally:
            loop.close()
        return True  # hand off—don't do the normal call
    # for non-async tests, let pytest handle them normally
