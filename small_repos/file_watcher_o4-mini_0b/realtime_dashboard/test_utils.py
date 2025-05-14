import pytest
import asyncio
from filewatcher.utils import normalize_event, inline_diff, retry_on_exception

def test_normalize_event():
    raw = {'x': 1}
    out = normalize_event(raw)
    assert out == raw and out is not raw

def test_inline_diff():
    old = "a\nb\nc\n"
    new = "a\nb changed\nc\n"
    diff = inline_diff(old, new)
    assert '-b\n' in diff or '+b changed\n' in diff

@pytest.mark.asyncio
async def test_retry_on_exception():
    calls = []

    @retry_on_exception(retries=2, backoff=0.01, exceptions=(ValueError,))
    async def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return "ok"

    res = await flaky()
    assert res == "ok"
    assert len(calls) == 2
