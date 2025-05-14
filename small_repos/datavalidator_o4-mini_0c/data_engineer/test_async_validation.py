import pytest
import asyncio
from etl_validator.schema import SchemaDefinition
from etl_validator.validator import Validator

class DummyExternal:
    def __init__(self, bad_values):
        self.bad = bad_values

    async def __call__(self, field, value):
        await asyncio.sleep(0)
        return value not in self.bad

@pytest.mark.anyio
async def test_async_validation_pass(schema_def_async):
    ext = DummyExternal(bad_values=['bad'])
    val = Validator(schema_def_async, external_validator=ext)
    rec = {'customer_id': 'good', 'order_id': '100'}
    result = await val.validate_async(rec)
    assert result.success

@pytest.mark.anyio
async def test_async_validation_fail(schema_def_async):
    ext = DummyExternal(bad_values=['bad'])
    val = Validator(schema_def_async, external_validator=ext)
    rec = {'customer_id': 'bad', 'order_id': '100'}
    result = await val.validate_async(rec)
    assert not result.success
    assert any(e['code'] == 'EXTERNAL' for e in result.errors)
