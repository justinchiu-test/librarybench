import pytest
import asyncio
from watcher.watcher import Watcher

@pytest.mark.asyncio
async def test_handler_retry(monkeypatch, tmp_path):
    dir1 = tmp_path / 'd'
    dir1.mkdir()
    f = dir1 / 'x.txt'
    events = []
    call_count = {'cnt': 0}
    def flaky_handler(path, event):
        call_count['cnt'] += 1
        if call_count['cnt'] < 3:
            raise PermissionError("transient")
        events.append((path, event))
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01,
                debounce_interval=0, max_retries=5, retry_delay=0.01)
    w.register_handler('create', flaky_handler)
    task = asyncio.create_task(w.watch())
    f.write_text('foo')
    await asyncio.sleep(0.1)
    task.cancel()
    await asyncio.sleep(0)
    assert call_count['cnt'] >= 3
    assert any(e[1] == 'create' for e in events)
