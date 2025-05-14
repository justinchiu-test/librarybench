import pytest
import asyncio
import os
from watcher import Watcher
from pathlib import Path
from watchdog.events import FileModifiedEvent

@pytest.mark.asyncio
async def test_modify_event_triggers(monkeypatch, tmp_path):
    # Prepare directory and file
    dir_path = tmp_path / "docs"
    dir_path.mkdir()
    file_path = dir_path / "doc.md"
    file_path.write_text("v1\n")
    # Setup watcher
    watcher = Watcher([str(dir_path)], ["http://example.com"])
    sent = []
    async def fake_send(payload):
        sent.append(payload)
    watcher.webhook.send = fake_send
    # Simulate modify event via handler
    from watcher import WatchHandler
    handler = WatchHandler(watcher.queue, watcher.filter, watcher.inline, watcher.log.logger)
    # Write new content then fire event
    file_path.write_text("v1\nv2\n")
    handler.on_any_event(FileModifiedEvent(str(file_path)))
    evt = await watcher.queue.get()
    await watcher._send_with_retry({"event": evt}, retries=1, delay=0)
    assert sent, "Expected webhook send"
    assert "v2" in sent[0]["event"]["diff"]
