import asyncio
import pytest
from filewatcher.webhook_integration import WebhookIntegration

@pytest.mark.asyncio
async def test_post_event_and_last_event():
    wh = WebhookIntegration("http://localhost")
    event = {"a": 1}
    ok = await wh.post_event(event)
    assert ok is True
    last = wh.last_event()
    assert '"a": 1' in last
