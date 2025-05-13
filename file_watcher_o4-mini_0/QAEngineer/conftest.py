import pytest
import asyncio
import inspect

def pytest_configure(config):
    # register the asyncio marker so pytest doesn't warn about it
    config.addinivalue_line("markers", "asyncio: mark test to be run under asyncio")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    # if the test is marked asyncio, run it on a fresh event loop
    if "asyncio" in pyfuncitem.keywords:
        func = pyfuncitem.obj
        loop = asyncio.new_event_loop()
        try:
            # Only pass kwargs that the test function actually accepts
            sig = inspect.signature(func)
            kwargs = {
                name: value
                for name, value in pyfuncitem.funcargs.items()
                if name in sig.parameters
            }
            loop.run_until_complete(func(**kwargs))
        finally:
            loop.close()
        # indicate we've handled the call
        return True
