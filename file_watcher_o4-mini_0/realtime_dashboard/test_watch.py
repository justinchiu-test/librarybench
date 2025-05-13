import pytest
import asyncio
import os
from filewatcher.watch import RecursiveDirectoryWatch
from filewatcher.filter_rules import DynamicFilterRules
from filewatcher.event_detection import HighLevelEventDetection
from filewatcher.webhook_integration import WebhookIntegration

@pytest.mark.asyncio
async def test_recursive_watch(tmp_path):
    root = tmp_path / "root"
    sub = root / "sub"
    sub.mkdir(parents=True)
    f1 = sub / "a.txt"
    f1.write_text("1")
    rules = DynamicFilterRules()
    rules.add_include("*.txt")
    det = HighLevelEventDetection()
    wh = WebhookIntegration("http://x")
    watch = RecursiveDirectoryWatch([str(root)], rules, det, webhook=wh)
    evs = []
    async for ev in watch.watch():
        evs.append(ev)
    assert len(evs) == 1
    assert evs[0]['type'].name == "MODIFY"
