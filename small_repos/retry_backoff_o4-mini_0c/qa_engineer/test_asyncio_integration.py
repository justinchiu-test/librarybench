import asyncio
import pytest
from retry_toolkit.asyncio_integration import async_retry

@pytest.mark.asyncio
async def test_async_retry_success():
    calls = []
    @async_retry(max_attempts=3)
    async def may_succeed():
        calls.append(1)
        if len(calls) < 2:
            raise Exception("fail")
        return "ok"
    result, history = await may_succeed()
    assert result == "ok"
    assert history == [("fail", 1), ("success", 2)]

@pytest.mark.asyncio
async def test_async_retry_all_fail():
    @async_retry(max_attempts=2, backoff=lambda x: asyncio.sleep(0))
    async def always_fail():
        raise Exception("err")
    with pytest.raises(Exception) as exc:
        await always_fail()
    assert "All 2 attempts failed" in str(exc.value)
