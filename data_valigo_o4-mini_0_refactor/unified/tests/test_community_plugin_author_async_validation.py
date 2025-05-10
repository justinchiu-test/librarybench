import pytest
import asyncio
from unified.src.community_plugin_author.validator.plugins import register_rule
from unified.src.community_plugin_author.validator.validation import Validator, AsyncValidationError

@register_rule('sync_rule')
def sync_rule(v, ctx):
    return v * 2

@register_rule('async_rule')
async def async_rule(v, ctx):
    await asyncio.sleep(0.01)
    return v + 3

def test_validator_sync():
    val = Validator()
    assert val.validate('sync_rule', 5) == 10

def test_validator_async_method():
    # Run async validation in a synchronous context
    val = Validator()
    res = asyncio.run(val.validate_async('async_rule', 7))
    assert res == 10

def test_validator_missing_rule():
    val = Validator()
    with pytest.raises(AsyncValidationError):
        val.validate('no_such', 1)
