import pytest
import asyncio
import os
from filewatcher.async_api import AsyncIOAPI
from filewatcher.filter_rules import DynamicFilterRules
from filewatcher.event_detection import HighLevelEventDetection
from filewatcher.webhook_integration import WebhookIntegration

@pytest.mark.asyncio
async def test_watch_yields_high_event(tmp_path):
    root = tmp_path / "d"
    root.mkdir()
    f = root / "file.txt"
    f.write_text("hello")
    rules = DynamicFilterRules()
    rules.add_include("*.txt")
    det = HighLevelEventDetection()
    wh = WebhookIntegration("http://x")
    api = AsyncIOAPI([str(root)], rules, det, webhook=wh)
    events = []
    async for ev in api.watch():
        events.append(ev)
    assert events
    assert 'type' in events[0]
    assert wh.last_event() is not None
