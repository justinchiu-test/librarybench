import pytest
import asyncio
import tempfile
import os
from watcher import Watcher, WatchHandler, DynamicFilterRules, InlineDiffs, LoggingSupport
from watchdog.events import FileCreatedEvent

@pytest.mark.asyncio
async def test_handler_and_processing(tmp_path, monkeypatch):
    # Setup temp dir and file
    temp_dir = tmp_path / "docs"
    temp_dir.mkdir()
    test_file = temp_dir / "test.md"
    test_file.write_text("first\n")
    # Setup watcher
    watcher = Watcher([str(temp_dir)], ["http://example.com"])
    # Patch webhook.send
    sent = []
    async def fake_send(payload):
        sent.append(payload)
    watcher.webhook.send = fake_send
    # Create handler and simulate event
    handler = WatchHandler(watcher.queue, watcher.filter, watcher.inline, watcher.log.logger)
    handler.on_any_event(FileCreatedEvent(str(test_file)))
    # Process one event
    evt = await watcher.queue.get()
    await watcher._send_with_retry({"event": evt}, retries=1, delay=0)
    assert sent, "No payload sent"
    payload = sent[0]
    assert payload["event"]["path"] == str(test_file)
    assert payload["event"]["diff"] != ""
