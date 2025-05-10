import pytest
import asyncio
from unified.src.security_specialist.securedata.validation import Rule, AsyncRule, ValidationEngine

class AlwaysTrueRule(Rule):
    def validate(self, value):
        return True

class AlwaysFalseRule(Rule):
    def validate(self, value):
        return False

class AsyncTrueRule(AsyncRule):
    async def validate_async(self, value):
        await asyncio.sleep(0)
        return True

def test_sync_validation():
    ve = ValidationEngine()
    ve.register_rule('signup', AlwaysTrueRule('t1'))
    ve.register_rule('signup', AlwaysFalseRule('t2'))
    ve.set_profile('signup')
    results = ve.validate('any')
    assert results == [('t1', True), ('t2', False)]

def test_async_validation():
    # Test asynchronous validation in synchronous context
    ve = ValidationEngine()
    ve.register_rule('admin', AlwaysTrueRule('sync'))
    ve.register_rule('admin', AsyncTrueRule('async'))
    ve.set_profile('admin')
    results = asyncio.run(ve.validate_async('x'))
    assert ('sync', True) in results
    assert ('async', True) in results
