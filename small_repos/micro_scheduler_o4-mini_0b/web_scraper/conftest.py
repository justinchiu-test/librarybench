import asyncio
import pytest

def pytest_configure(config):
    # register the asyncio marker so pytest won’t complain
    config.addinivalue_line("markers", "asyncio: mark test to be run with asyncio")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    # if the test has the @pytest.mark.asyncio decorator, run it in the loop
    if "asyncio" in pyfuncitem.keywords:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        testfunc = pyfuncitem.obj
        # collect the fixtures for the test
        kwargs = {
            name: pyfuncitem.funcargs[name] 
            for name in pyfuncitem._fixtureinfo.argnames
        }
        loop.run_until_complete(testfunc(**kwargs))
        return True
    # otherwise let pytest handle it normally
    return None
