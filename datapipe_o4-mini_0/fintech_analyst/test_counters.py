import pytest
from counters import CounterManager

def test_increment_and_get():
    cm = CounterManager()
    assert cm.get('ticks') == 0
    cm.increment('ticks')
    cm.increment('successes')
    cm.increment('failures')
    assert cm.get('ticks') == 1
    assert cm.get('successes') == 1
    assert cm.get('failures') == 1

def test_get_all():
    cm = CounterManager()
    cm.increment('ticks')
    all_counts = cm.get_all()
    assert all_counts == {'ticks': 1, 'successes': 0, 'failures': 0}

def test_invalid_counter():
    cm = CounterManager()
    with pytest.raises(KeyError):
        cm.increment('unknown')
    with pytest.raises(KeyError):
        cm.get('unknown')
