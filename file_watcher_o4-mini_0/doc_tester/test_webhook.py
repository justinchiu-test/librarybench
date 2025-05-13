import pytest
import asyncio
from watcher import WebhookIntegration

class DummyResponse:
    async def text(self):
        return "OK"

class DummySession:
    def __init__(self):
        self.posts = []
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json):
        self.posts.append((url, json))
        return DummyResponse()

@pytest.mark.asyncio
async def test_webhook_send(monkeypatch):
    we = WebhookIntegration(["http://example.com/hook"])
    dummy = DummySession()
    monkeypatch.setattr("aiohttp.ClientSession", lambda: dummy)
    payload = {"event": {"type": "test", "path": "/tmp/file.md"}}
    await we.send(payload)
    assert dummy.posts == [("http://example.com/hook", payload)]
