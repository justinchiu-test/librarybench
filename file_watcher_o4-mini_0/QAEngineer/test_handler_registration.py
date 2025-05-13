import pytest
import time
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_handler_called(tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    f = dir1 / 'x.txt'
    events = []
    def handler(path, event):
        events.append((path, event))
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0)
    w.register_handler('create', handler)
    task = asyncio.create_task(w.watch())
    # create file
    f.write_text('foo')
    await asyncio.sleep(0.05)
    task.cancel()
    await asyncio.sleep(0)
    assert any(str(f) == p and e == 'create' for p, e in events)
