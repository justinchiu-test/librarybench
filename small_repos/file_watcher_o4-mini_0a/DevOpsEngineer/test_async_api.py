import pytest
import asyncio
from file_watcher.core import FileWatcher

@pytest.mark.asyncio
async def test_trigger_event_async():
    fw = FileWatcher()
    ev = await fw.trigger_event_async('afile', 'type')
    assert ev is not None
    assert ev.path == 'afile'
    assert ev.type == 'type'
