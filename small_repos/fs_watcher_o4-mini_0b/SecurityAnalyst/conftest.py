import pytest
import asyncio

@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
