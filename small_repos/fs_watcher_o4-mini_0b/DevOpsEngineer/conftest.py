import pytest
import asyncio

def pytest_configure(config):
    # Register the 'asyncio' marker to avoid unknown‐mark warnings.
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to be run as an asyncio coroutine"
    )

def pytest_pyfunc_call(pyfuncitem):
    """
    Execute async test functions in their own event loop if no pytest‐asyncio plugin is present.
    """
    testfunc = pyfuncitem.obj
    if asyncio.iscoroutinefunction(testfunc):
        # Gather fixture arguments
        funcargs = pyfuncitem.funcargs
        # Create a fresh event loop for this test
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            # Run the coroutine
            loop.run_until_complete(testfunc(**funcargs))
        finally:
            loop.close()
        # Handled the call ourselves
        return True
    # Let pytest handle normal (non‐async) tests
    return None
