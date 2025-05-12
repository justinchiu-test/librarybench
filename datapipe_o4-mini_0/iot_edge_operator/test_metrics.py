import pytest
from pipeline.metrics import create_counter, _counters

def test_create_counter_unique():
    c1 = create_counter('test')
    c2 = create_counter('test')
    assert c1 is c2

def test_counter_inc_and_get():
    c = create_counter('count')
    initial = c.get_count()
    c.inc()
    c.inc(2)
    assert c.get_count() == initial + 3

def test_monitor_pipeline(capsys):
    # ensure counters exist
    create_counter('m1').inc()
    create_counter('m2').inc(2)
    from pipeline.metrics import monitor_pipeline
    monitor_pipeline()
    captured = capsys.readouterr()
    assert 'Counter m1: 1' in captured.out
    assert 'Counter m2: 2' in captured.out
