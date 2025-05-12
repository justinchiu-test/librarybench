import pytest
import time
import logging
import argparse
from streaming import (
    tumbling_window,
    sliding_window,
    add_serializer,
    get_serializer,
    throttle_upstream,
    watermark_event_time,
    halt_on_error,
    skip_error,
    setup_logging,
    cli_manage,
    parallelize_stages,
)

def test_tumbling_window():
    readings = [
        {"timestamp":1, "value":10},
        {"timestamp":2, "value":20},
        {"timestamp":5, "value":30},
        {"timestamp":7, "value":40},
    ]
    windows = list(tumbling_window(readings, window_size=3))
    assert len(windows) == 3
    assert windows[0] == [
        {"timestamp":1, "value":10},
        {"timestamp":2, "value":20}
    ]
    assert windows[1] == [{"timestamp":5, "value":30}]
    assert windows[2] == [{"timestamp":7, "value":40}]

def test_sliding_window():
    readings = [
        {"timestamp":1, "value":2},
        {"timestamp":2, "value":4},
        {"timestamp":3, "value":6},
        {"timestamp":4, "value":8},
    ]
    results = list(sliding_window(readings, window_size=2, step=1))
    assert results[0]["end"] == 3
    assert abs(results[0]["average"] - 5.0) < 1e-6
    assert results[1]["end"] == 4
    assert abs(results[1]["average"] - 7.0) < 1e-6

def test_add_serializer():
    class Dummy: pass
    serializers = add_serializer("dummy", Dummy)
    assert serializers["dummy"] is Dummy
    assert get_serializer("dummy") is Dummy

def test_throttle_upstream():
    @throttle_upstream(max_calls=1)
    def fast(x):
        return x
    start = time.time()
    res1 = fast(1)
    res2 = fast(2)
    end = time.time()
    assert res1 == 1
    assert res2 == 2
    assert end - start >= 0.1

def test_watermark_event_time():
    readings = [{"timestamp":5, "value":100}]
    results = list(watermark_event_time(readings, delay=2))
    assert results[0]["watermark"] == 3
    assert results[0]["value"] == 100

def test_skip_and_halt_on_error(caplog):
    @skip_error
    def bad(x):
        raise ValueError("bad")
    @halt_on_error
    def bad2(x):
        raise ValueError("fatal")
    caplog.set_level(logging.WARNING)
    res = bad(10)
    assert res is None
    assert "Skipping error in bad" in caplog.text
    with pytest.raises(ValueError):
        bad2(10)

def test_setup_logging():
    logger = setup_logging(logging.DEBUG)
    assert logger.level == logging.DEBUG
    hcount = len(logger.handlers)
    logger2 = setup_logging(logging.INFO)
    assert len(logger2.handlers) == hcount
    assert logger2.level == logging.INFO

def test_cli_manage():
    parser = cli_manage()
    assert isinstance(parser, argparse.ArgumentParser)
    sub = parser.parse_args(["scaffold"])
    assert sub.command == "scaffold"
    sub = parser.parse_args(["start"])
    assert sub.command == "start"
    sub = parser.parse_args(["stop"])
    assert sub.command == "stop"
    sub = parser.parse_args(["health"])
    assert sub.command == "health"

def test_parallelize_stages():
    def stage1(q):
        q.put("a")
    def stage2(q):
        q.put("b")
    procs, q = parallelize_stages([stage1, stage2])
    time.sleep(0.2)
    results = set()
    while not q.empty():
        results.add(q.get())
    assert results == {"a", "b"}
    assert len(procs) == 2
    for p in procs:
        p.terminate()
        p.join()
