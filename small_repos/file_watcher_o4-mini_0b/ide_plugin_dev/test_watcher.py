import asyncio
import pytest
from filewatcher.watcher import FileWatcher
from filewatcher.filters import FilterRules

@pytest.mark.asyncio
async def test_detect_create_delete(tmp_path):
    root = tmp_path / 'proj'
    root.mkdir()
    events = []
    watcher = FileWatcher(str(root), poll_interval=0.1)
    watcher.subscribe(lambda ev: events.append(ev))
    await watcher.start()
    # create file
    f = root / 'a.txt'
    f.write_text('hello')
    await asyncio.sleep(0.2)
    # delete file
    f.unlink()
    await asyncio.sleep(0.2)
    await watcher.stop()
    types = [e.event_type for e in events]
    assert 'created' in types
    assert 'deleted' in types

@pytest.mark.asyncio
async def test_detect_modify_inline_diff(tmp_path):
    root = tmp_path / 'proj2'
    root.mkdir()
    f = root / 'b.txt'
    f.write_text('line1\nline2\n')
    events = []
    watcher = FileWatcher(str(root), poll_interval=0.1)
    watcher.subscribe(lambda ev: events.append(ev))
    await watcher.start()
    # modify file
    f.write_text('line1\nline2 modified\n')
    await asyncio.sleep(0.2)
    await watcher.stop()
    mods = [e for e in events if e.event_type=='modified']
    assert len(mods) == 1
    diff = mods[0].diff
    assert 'line2' in diff
    assert 'line2 modified' in diff

@pytest.mark.asyncio
async def test_filter_rules(tmp_path):
    root = tmp_path / 'proj3'
    root.mkdir()
    d1 = root / 'node_modules'
    d1.mkdir()
    f1 = d1 / 'foo.js'
    f1.write_text('var a=1;')
    f2 = root / 'main.js'
    f2.write_text('var b=2;')
    filters = FilterRules()
    filters.add_exclude('node_modules')
    events = []
    watcher = FileWatcher(str(root), filters=filters, poll_interval=0.1)
    watcher.subscribe(lambda ev: events.append(ev))
    await watcher.start()
    await asyncio.sleep(0.2)
    await watcher.stop()
    paths = [e.src_path for e in events if e.event_type=='created']
    assert 'main.js' in paths
    assert 'node_modules/foo.js' not in paths
