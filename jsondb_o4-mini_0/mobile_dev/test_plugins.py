import pytest
from journaling.plugins import PluginManager

class Dummy:
    def __init__(self):
        self.log = []

    def on_before_upsert(self, entry):
        self.log.append(('before', entry['id']))

    def on_after_upsert(self, entry):
        self.log.append(('after', entry['id']))

    def on_delete(self, entry):
        self.log.append(('delete', entry['id']))

def test_plugin_hooks(tmp_path, os, time):
    from journaling.db import JournalDB
    key = os.urandom(32)
    db = JournalDB(str(tmp_path), key)
    plugin = Dummy()
    db.registerPlugin(plugin)
    entry = {
        'id': 'x',
        'content': 'hi',
        'tags': [],
        'attachments': [],
        'metadata': {},
        'created_at': time.time(),
        'updated_at': time.time()
    }
    db.upsert(entry)
    assert ('before', 'x') in plugin.log
    assert ('after', 'x') in plugin.log
    db.delete_by_id('x')
    assert ('delete', 'x') in plugin.log
