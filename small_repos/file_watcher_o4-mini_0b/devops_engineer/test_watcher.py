import asyncio
import os
import tempfile
import time
import pytest
from filewatcher.watcher import AsyncFileWatcher

@pytest.mark.asyncio
async def test_create_modify_delete(tmp_path):
    file = tmp_path / "test.txt"
    events = []
    watcher = AsyncFileWatcher(paths=[str(tmp_path)], includes=["*.txt"], interval=0.1)
    watcher.register_handler(lambda e: events.append(e))
    await watcher.start()
    # create
    file.write_text("hello")
    await asyncio.sleep(0.2)
    # modify
    file.write_text("hello world")
    await asyncio.sleep(0.2)
    # delete
    file.unlink()
    await asyncio.sleep(0.2)
    await watcher.stop()
    types = [e["type"] for e in events]
    assert "created" in types
    assert "modified" in types
    assert "deleted" in types
    # check diff for modify
    modify_events = [e for e in events if e["type"]=="modified"]
    assert modify_events and "hello world" in modify_events[0]["diff"]

@pytest.mark.asyncio
async def test_dynamic_filters(tmp_path):
    a = tmp_path / "a.log"
    b = tmp_path / "b.txt"
    events = []
    watcher = AsyncFileWatcher(paths=[str(tmp_path)], includes=["*.txt"], interval=0.1)
    watcher.register_handler(lambda e: events.append(e))
    await watcher.start()
    # only txt
    a.write_text("log")
    b.write_text("txt")
    await asyncio.sleep(0.2)
    assert any(e["type"]=="created" and e["path"].endswith(".txt") for e in events)
    # now include .log
    watcher.add_include("*.log")
    events.clear()
    c = tmp_path / "c.log"
    c.write_text("new")
    await asyncio.sleep(0.2)
    await watcher.stop()
    assert any(e["path"].endswith(".log") for e in events)
