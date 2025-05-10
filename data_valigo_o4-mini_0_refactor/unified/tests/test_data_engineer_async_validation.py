import pytest
import asyncio
from unified.src.data_engineer.dataschema.validation import AsyncRule

def test_sync_rule():
    def is_positive(x): return x > 0
    rule = AsyncRule(is_positive)
    assert rule.validate(5)
    assert not rule.validate(-1)
    # async
    result = asyncio.run(rule.validate_async(10))
    assert result

def test_async_rule():
    # Test async validation in a synchronous context
    async def check(x):
        await asyncio.sleep(0.01)
        return x == 'ok'
    rule = AsyncRule(check)
    result_ok = asyncio.run(rule.validate_async('ok'))
    assert result_ok
    result_no = asyncio.run(rule.validate_async('no'))
    assert not result_no
    # validate should still run synchronously
    assert not rule.validate('no')
