import pytest
from telemetry.registry import AsyncRegistryClient

@pytest.mark.asyncio
async def test_validate_certificate():
    client = AsyncRegistryClient({'a', 'b'})
    assert await client.validate_certificate('a')
    assert not await client.validate_certificate('c')
