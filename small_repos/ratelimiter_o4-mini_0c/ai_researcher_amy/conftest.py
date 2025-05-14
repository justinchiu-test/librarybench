import pytest
import asyncio
from ratelimiter.token_bucket import TokenBucket

@pytest.fixture
def rate_limiter_fixture():
    def _create(rate, capacity):
        return TokenBucket(rate, capacity)
    return _create

def pytest_pyfunc_call(pyfuncitem):
    """
    A minimal hook to run async test functions without requiring pytest-asyncio.
    """
    if asyncio.iscoroutinefunction(pyfuncitem.obj):
        # Collect fixture arguments
        funcargs = {
            name: pyfuncitem.funcargs[name]
            for name in pyfuncitem._fixtureinfo.argnames
        }
        # Create a fresh event loop to run the coroutine
        loop = asyncio.new_event_loop()
        try:
            coro = pyfuncitem.obj(**funcargs)
            loop.run_until_complete(coro)
        finally:
            loop.close()
        return True
