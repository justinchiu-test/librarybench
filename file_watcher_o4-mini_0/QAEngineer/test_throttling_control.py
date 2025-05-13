import pytest
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_burst_throttling(tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    f = dir1 / 'x.txt'
    events = []
    def handler(path, event):
        events.append((path, event))
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0.05)
    w.register_handler('modify', handler)
    task = asyncio.create_task(w.watch())
    f.write_text('1')
    await asyncio.sleep(0.02)
    f.write_text('2')
    await asyncio.sleep(0.02)
    f.write_text('3')
    await asyncio.sleep(0.1)
    task.cancel()
    await asyncio.sleep(0)
    # only one modify due to debounce
    mods = [e for e in events if e[1] == 'modify']
    assert len(mods) == 1
