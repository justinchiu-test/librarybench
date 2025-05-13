import pytest
import inspect
import asyncio

def pytest_configure(config):
    # register the asyncio marker so pytest doesn't warn
    config.addinivalue_line(
        "markers", "asyncio: mark test to be run with asyncio (handled by anyio)"
    )

def pytest_collection_modifyitems(config, items):
    # any test marked with @pytest.mark.asyncio should also be run under anyio
    for item in items:
        if item.get_closest_marker("asyncio"):
            item.add_marker(pytest.mark.anyio)

def pytest_pyfunc_call(pyfuncitem):
    """
    Detect coroutine test functions and execute them in an asyncio event loop,
    so that async def tests (e.g., pytest.mark.asyncio) are handled properly.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Prepare arguments for the test function (fixtures)
        funcargs = {arg: pyfuncitem.funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        # Create a new event loop for isolation
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_func(**funcargs))
            return True
        finally:
            loop.close()
    # Non-async tests are handled by the default pytest machinery
    return None
