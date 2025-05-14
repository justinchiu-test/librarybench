import pytest
import asyncio
import os
import tempfile
from filewatcher import FileWatcher
from event_history_store import EventHistoryStore
from cicd import CiCdTrigger

@pytest.mark.asyncio
async def test_hidden_file_filter(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    f1 = d / ".hidden"
    f1.write_text("secret")
    f2 = d / "visible.txt"
    f2.write_text("data")
    watcher = FileWatcher(str(d), hidden_filter=True, dry_run=True)
    events = [e async for e in watcher.scan()]
    assert all(not e[0].endswith(".hidden") for e in events)
    assert any(e[0].endswith("visible.txt") for e in events)

@pytest.mark.asyncio
async def test_symlink_follow(tmp_path):
    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d1.mkdir(); d2.mkdir()
    f = d2 / "file.txt"
    f.write_text("hi")
    link = d1 / "link"
    os.symlink(str(d2), str(link))
    # without follow
    watcher1 = FileWatcher(str(d1), follow_symlinks=False, dry_run=True)
    ev1 = [e async for e in watcher1.scan()]
    assert not ev1
    # with follow
    watcher2 = FileWatcher(str(d1), follow_symlinks=True, dry_run=True)
    ev2 = [e async for e in watcher2.scan()]
    assert any("file.txt" in e[0] for e in ev2)

@pytest.mark.asyncio
async def test_handler_and_history(tmp_path):
    d = tmp_path / "x"
    d.mkdir()
    f = d / "new.csv"
    f.write_text("1,2,3")
    history = EventHistoryStore()
    results = []
    async def handler(path):
        results.append(path)
    watcher = FileWatcher(str(d), history_store=history, dry_run=False)
    watcher.register_handler('created', handler)
    # simulate scan and handle
    events = [e async for e in watcher.scan()]
    for path, etype, ts in events:
        await watcher._handle_event(path, etype, ts)
    assert any("new.csv" in r for r in results)
    q = history.query(event_type="created")
    assert any("new.csv" in e[0] for e in q)

@pytest.mark.asyncio
async def test_dry_run_skips_actions(tmp_path):
    d = tmp_path / "y"
    d.mkdir()
    f = d / "file.json"
    f.write_text("{}")
    history = EventHistoryStore()
    results = []
    async def handler(path):
        results.append(path)
    trigger = CiCdTrigger("echo")
    watcher = FileWatcher(str(d), history_store=history, dry_run=True, cicd_triggers=[trigger])
    watcher.register_handler('created', handler)
    events = [e async for e in watcher.scan()]
    for path, etype, ts in events:
        await watcher._handle_event(path, etype, ts)
    assert results == []
    # history still logs
    q = history.query(event_type="created")
    assert q

