import pytest
from config_watcher.webhook_integration import WebhookClient

class FakeResponse:
    def __init__(self, status):
        self.status = status
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

class FakeSession:
    def __init__(self, statuses):
        self.statuses = statuses
        self.calls = 0
        self.posts = []
    def post(self, url, json):
        status = self.statuses[min(self.calls, len(self.statuses)-1)]
        self.calls += 1
        self.posts.append((url, json))
        return FakeResponse(status)
    async def close(self):
        pass

@pytest.mark.asyncio
async def test_send_success():
    client = WebhookClient('http://x', max_retries=2)
    client.session = FakeSession([200])
    result = await client.send({'a': 1})
    assert result
    assert client.session.posts

@pytest.mark.asyncio
async def test_send_failure():
    client = WebhookClient('http://x', max_retries=2, base_backoff=0)
    client.session = FakeSession([500, 500, 500])
    result = await client.send({'a': 2})
    assert not result
