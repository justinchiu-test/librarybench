import asyncio
import pytest
from filewatcher.webhook import WebhookIntegration

class DummySession:
    def __init__(self, statuses):
        self.statuses = statuses
        self.calls = 0
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json):
        class Resp:
            def __init__(self, status):
                self.status = status
            async def __aenter__(self_inner):
                return self_inner
            async def __aexit__(self_inner, exc_type, exc, tb):
                pass
        st = self.statuses[self.calls]
        self.calls += 1
        return Resp(st)

@pytest.mark.asyncio
async def test_retry_logic(monkeypatch):
    statuses = [500, 200]
    sess = DummySession(statuses)
    calls = []
    class DummyIntegration(WebhookIntegration):
        async def _post_with_retry(self, url, payload):
            calls.append(url)
            return await super()._post_with_retry(url, payload)
    wi = DummyIntegration(["http://example.com"], retry_attempts=2, backoff_factor=0)
    async def dummy_session():
        return sess
    monkeypatch.setattr("aiohttp.ClientSession", lambda: sess)
    await wi.send({"k": "v"})
    assert sess.calls == 2
