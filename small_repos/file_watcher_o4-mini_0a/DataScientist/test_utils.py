import pytest
import asyncio
from utils import retry

@pytest.mark.asyncio
async def test_retry_success():
    calls = {'count': 0}
    @retry(Exception, tries=3, delay=0, backoff=1)
    async def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise Exception("fail")
        return "ok"
    result = await flaky()
    assert result == "ok"
    assert calls['count'] == 3

@pytest.mark.asyncio
async def test_retry_no_fail():
    calls = {'count': 0}
    @retry(Exception, tries=2, delay=0, backoff=1)
    async def good():
        calls['count'] += 1
        return "fine"
    result = await good()
    assert result == "fine"
    assert calls['count'] == 1
