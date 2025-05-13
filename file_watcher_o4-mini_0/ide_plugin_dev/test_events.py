import time
from filewatcher.events import Event

def test_event_creation():
    ev = Event('created', 'foo.txt')
    assert ev.event_type == 'created'
    assert ev.src_path == 'foo.txt'
    assert ev.dest_path is None
    assert ev.diff is None
    d = ev.to_dict()
    assert d['event_type'] == 'created'
    assert d['src_path'] == 'foo.txt'
    assert 'timestamp' in d
    assert isinstance(d['timestamp'], float)
