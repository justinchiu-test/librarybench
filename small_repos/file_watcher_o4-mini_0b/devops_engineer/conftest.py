import asyncio
import pytest

def pytest_configure(config):
    # register the asyncio marker so pytest won't warn about it
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to be run on an asyncio event loop"
    )

@pytest.fixture
def loop():
    """
    Provide an asyncio loop fixture (needed by aiohttp_server fixture).
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    If the test function is a coroutine function, run it to completion.
    This lets us run async def tests marked with @pytest.mark.asyncio
    without needing pytest-asyncio installed.
    """
    testfunc = pyfuncitem.obj
    if asyncio.iscoroutinefunction(testfunc):
        # collect fixtures for the function
        fixturenames = pyfuncitem._fixtureinfo.argnames
        funcargs = {name: pyfuncitem.funcargs[name] for name in fixturenames}
        loop = funcargs.get("loop", asyncio.get_event_loop())
        loop.run_until_complete(testfunc(**funcargs))
        return True  # we've handled the call
    # let pytest handle non-async functions normally
    return None

# Provide a working aiohttp_server fixture for the webhook tests
import aiohttp
from aiohttp import web

@pytest.fixture
def aiohttp_server(loop, free_tcp_port_factory):
    def _make_server(app: web.Application):
        async def _serve():
            runner = web.AppRunner(app)
            await runner.setup()
            port = free_tcp_port_factory()
            site = web.TCPSite(runner, "127.0.0.1", port)
            await site.start()
            class Server:
                def make_url(self, path: str) -> str:
                    return f"http://127.0.0.1:{port}{path}"
            return Server()
        # return the coroutine so the test can "server = await aiohttp_server(app)"
        return _serve()
    return _make_server
