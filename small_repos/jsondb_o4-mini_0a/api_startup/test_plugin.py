import pytest
from db_engine import DBEngine

def test_plugin_hooks():
    engine = DBEngine(path=':memory:', encryption_key=b'k')
    events = []
    class HookPlugin:
        def register(self, eng):
            self.eng = eng
        def on_upsert(self, eid, evt):
            events.append((eid, evt['userID']))
    plugin = HookPlugin()
    engine.registerPlugin(plugin)
    eid = engine.upsert({'timestamp': 1, 'userID': 'p1', 'eventType': 't'})
    assert events == [(eid, 'p1')]
    # batch upsert
    events.clear()
    ids = engine.batchUpsert([
        {'timestamp': 2, 'userID': 'p2', 'eventType': 't'},
        {'timestamp': 3, 'userID': 'p3', 'eventType': 't'}
    ])
    assert len(events) == 2
    assert [e[0] for e in events] == ids
