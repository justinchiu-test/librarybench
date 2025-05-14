import pytest
import asyncio
import time
import logging
from config_watcher.watcher import ConfigEventHandler
from config_watcher.filter_rules import FilterRules

class DummyWebhook:
    def __init__(self):
        self.sent = []
    async def send(self, payload):
        self.sent.append(payload)
        return True

@pytest.fixture
def handler(tmp_path):
    fl = FilterRules()
    fl.include('*')
    webhook = DummyWebhook()
    logger = logging.getLogger('test')
    handler = ConfigEventHandler(fl, webhook, logger)
    return handler

def test_on_created(tmp_path, handler):
    p = tmp_path / "a.txt"
    p.write_text("hello")
    class E: is_directory=False; src_path=str(p)
    handler.on_created(E)
    time.sleep(0.1)
    assert handler.webhook.sent[0]['action'] == 'created'

def test_on_modified(tmp_path, handler):
    p = tmp_path / "b.txt"
    p.write_text("line1\n")
    class E: is_directory=False; src_path=str(p)
    handler.on_modified(E)
    time.sleep(0.1)
    p.write_text("line1\nline2\n")
    handler.on_modified(E)
    time.sleep(0.1)
    mods = [d for d in handler.webhook.sent if d['action']=='modified']
    assert mods
    assert 'line2' in mods[-1]['detail']
