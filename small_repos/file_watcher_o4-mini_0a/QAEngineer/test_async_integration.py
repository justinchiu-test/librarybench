import pytest
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_async_watch_stop(tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01)
    # start and then cancel immediately
    task = asyncio.create_task(w.watch())
    await asyncio.sleep(0.01)
    task.cancel()
    await asyncio.sleep(0)
    assert task.done()
