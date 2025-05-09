import pytest
import asyncio
from data_engineer.dataschema.validation import AsyncRule

def test_sync_rule():
    def is_positive(x): return x > 0
    rule = AsyncRule(is_positive)
    assert rule.validate(5)
    assert not rule.validate(-1)
    # async
    result = asyncio.get_event_loop().run_until_complete(rule.validate_async(10))
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
