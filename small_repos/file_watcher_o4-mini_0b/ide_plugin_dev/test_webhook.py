import json
import pytest
from aiohttp import ClientSession
from filewatcher.events import Event
from filewatcher.watcher import FileWatcher
from filewatcher.webhook import WebhookServer

@pytest.mark.asyncio
async def test_webhook_server(tmp_path):
    root = tmp_path / 'wproj'
    root.mkdir()
    watcher = FileWatcher(str(root), poll_interval=0.1)
    server = WebhookServer('127.0.0.1', 8081, watcher)
    await watcher.start()
    await server.start()
    session = ClientSession()
    resp = await session.get('http://127.0.0.1:8081/events')
    assert resp.status == 200
    ev = Event('created', 'foo.txt')
    await watcher.simulate_event(ev)
    line = await resp.content.readline()
    assert line.startswith(b'data:')
    data = json.loads(line.lstrip(b'data: ').decode())
    assert data['event_type'] == 'created'
    await resp.release()
    await session.close()
    await server.stop()
    await watcher.stop()
