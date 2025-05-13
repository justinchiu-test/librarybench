import pytest
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_history_integration(tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    f = dir1 / 'x.txt'
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0)
    task = asyncio.create_task(w.watch())
    f.write_text('data')
    await asyncio.sleep(0.05)
    task.cancel()
    await asyncio.sleep(0)
    hist = w.history.query(event_type='create')
    assert any(e['path'].endswith('x.txt') for e in hist)
