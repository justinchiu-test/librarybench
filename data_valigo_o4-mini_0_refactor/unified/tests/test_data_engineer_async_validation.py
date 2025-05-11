import pytest
import asyncio
# Ensure an event loop is available for async tests
asyncio.set_event_loop(asyncio.new_event_loop())
from unified.src.data_engineer import AsyncRule

def test_sync_rule():
    def is_positive(x): return x > 0
    rule = AsyncRule(is_positive)
    assert rule.validate(5)
    assert not rule.validate(-1)
    # async: run using a fresh event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(rule.validate_async(10))
    assert result

@pytest.mark.asyncio
async def test_async_rule():
    async def check(x):
        await asyncio.sleep(0.01)
        return x == 'ok'
    rule = AsyncRule(check)
    assert await rule.validate_async('ok')
    assert not await rule.validate_async('no')
    # validate should run sync
    assert not rule.validate('no')
