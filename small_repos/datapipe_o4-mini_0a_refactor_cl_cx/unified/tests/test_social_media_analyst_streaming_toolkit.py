import pytest
import logging
import json
import multiprocessing
from social_media_analyst.streaming_toolkit import (
    tumbling_window, sliding_window, add_serializer,
    throttle_upstream, watermark_event_time,
    halt_on_error, skip_error, setup_logging,
    cli_manage, parallelize_stages, track_lineage
)


def test_tumbling_window():
    posts = [
        {'timestamp': 0, 'text': 'a'},
        {'timestamp': 30, 'text': 'b'},
        {'timestamp': 61, 'text': 'c'}
    ]
    windows = tumbling_window(posts)
    assert len(windows) == 2
    assert windows[0] == [{'timestamp': 0, 'text': 'a'}, {'timestamp': 30, 'text': 'b'}]
    assert windows[1] == [{'timestamp': 61, 'text': 'c'}]


def test_sliding_window():
    posts = [
        {'timestamp': 0, 'sentiment': 1.0},
        {'timestamp': 100, 'sentiment': 3.0},
        {'timestamp': 400, 'sentiment': 2.0},
    ]
    results = sliding_window(posts, window_size=200)
    # at ts=0: only one post -> avg=1
    assert results[0]['avg_sentiment'] == pytest.approx(1.0)
    # at ts=100: posts at 0 and 100 -> avg=2
    assert results[1]['avg_sentiment'] == pytest.approx(2.0)
    # at ts=400: only itself -> avg=2.0
    assert results[2]['avg_sentiment'] == pytest.approx(2.0)


def test_add_serializer():
    data = {'foo': 'bar'}
    serializer = add_serializer(data)
    bjson = serializer.serialize('json')
    assert bjson.startswith(b'JSON:')
    parsed = json.loads(bjson[len(b'JSON:'):])
    assert parsed == data
    bavro = serializer.serialize('avro')
    assert bavro.startswith(b'AVRO:')
    bpar = serializer.serialize('parquet')
    assert bpar.startswith(b'PARQUET:')
    with pytest.raises(ValueError):
        serializer.serialize('xml')


def test_throttle_upstream():
    data = list(range(10))
    out = list(throttle_upstream(data, 3))
    assert out == [0, 1, 2]


def test_watermark_event_time():
    posts = [
        {'timestamp': 10},
        {'timestamp': 5},
        {'timestamp': 20},
    ]
    wms = watermark_event_time(posts, lateness=5)
    # max seen at first=10 -> 10-5=5
    assert wms[0] == 5
    # max still 10 -> 10-5=5
    assert wms[1] == 5
    # max now 20 -> 20-5=15
    assert wms[2] == 15


def test_halt_on_error():
    @halt_on_error
    def f(x):
        if x == 0:
            raise RuntimeError("fail")
        return x
    with pytest.raises(RuntimeError):
        f(0)
    assert f(1) == 1


def test_skip_error(caplog):
    logger = setup_logging()
    caplog.set_level(logging.WARNING)
    @skip_error
    def g(x):
        if x == 0:
            raise ValueError("oops")
        return x*2
    assert g(0) is None
    assert "Skipping due to error" in caplog.text
    assert g(2) == 4


def test_setup_logging():
    logger = setup_logging()
    assert logger.level == logging.DEBUG


def test_cli_manage_start(capsys):
    cli_manage(['start'])
    captured = capsys.readouterr()
    assert "Pipeline started" in captured.out

def test_cli_manage_monitor(capsys):
    cli_manage(['monitor'])
    captured = capsys.readouterr()
    assert "Monitoring throughput" in captured.out

def test_cli_manage_logs(capsys):
    cli_manage(['logs'])
    captured = capsys.readouterr()
    assert "Tailing logs" in captured.out

def test_parallelize_stages():
    # define simple functions
    def inc(x): return [i+1 for i in x]
    def dbl(x): return [i*2 for i in x]
    data = [1, 2, 3]
    results = parallelize_stages([inc, dbl], data)
    # order corresponds
    assert results[0] == [2, 3, 4]
    assert results[1] == [2, 4, 6]

def test_track_lineage():
    post = {'text': 'hello'}
    p1 = track_lineage(post, 'step1')
    assert '_lineage' in p1 and p1['_lineage'] == ['step1']
    p2 = track_lineage(p1, 'step2')
    assert p2['_lineage'] == ['step1', 'step2']
