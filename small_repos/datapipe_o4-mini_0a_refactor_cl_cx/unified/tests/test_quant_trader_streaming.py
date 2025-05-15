import pytest
import time
import logging
import multiprocessing
from click.testing import CliRunner
import unified.quant_trader.streaming as streaming

def test_tumbling_window_count():
    records = [{'timestamp': i, 'price': i, 'volume': 1} for i in range(6)]
    res = streaming.tumbling_window(records, 2, by_time=False)
    assert len(res) == 3
    assert res[0] == {'open': 0, 'high': 1, 'low': 0, 'close': 1, 'volume': 2}

def test_tumbling_window_time():
    records = [{'timestamp': ts, 'price': ts, 'volume': 1} for ts in [1, 2, 3, 5, 6]]
    res = streaming.tumbling_window(records, 3, by_time=True)
    assert len(res) == 2
    assert res[0]['open'] == 1 and res[0]['close'] == 3
    assert res[1]['open'] == 5 and res[1]['close'] == 6

def test_sliding_window():
    records = [{'price': p} for p in [1, 2, 3, 4]]
    res = streaming.sliding_window(records, 3, 1)
    assert len(res) == 2
    assert res[0]['average'] == pytest.approx((1 + 2 + 3) / 3)

def test_serializer_registry():
    class S: pass
    s = S()
    streaming.add_serializer('dummy', s)
    assert streaming.get_serializer('dummy') is s

def test_watermark_event_time():
    records = [{'timestamp': t} for t in [1, 5, 10, 15]]
    res = streaming.watermark_event_time(records, allowed_lateness=5)
    assert all(r['timestamp'] >= 10 for r in res)
    assert len(res) == 2

def test_throttle_upstream(monkeypatch):
    calls = []
    fake_time = [0.0]
    def fake_time_func():
        return fake_time[0]
    def fake_sleep(duration):
        calls.append(duration)
        fake_time[0] += duration
    monkeypatch.setattr(time, 'time', fake_time_func)
    monkeypatch.setattr(time, 'sleep', fake_sleep)
    @streaming.throttle_upstream(2)
    def foo(x):
        return x
    assert foo(1) == 1
    fake_time[0] += 0.1
    assert foo(2) == 2
    # interval=0.5, elapsed=0.1 so sleep 0.4
    assert pytest.approx(calls[-1], 0.001) == 0.4

def test_halt_and_skip_error(caplog):
    @streaming.halt_on_error
    def f1():
        raise ValueError('oops')
    with pytest.raises(ValueError):
        f1()
    @streaming.skip_error
    def f2():
        raise RuntimeError('fail')
    caplog.set_level(logging.WARNING)
    res = f2()
    assert res is None
    assert 'Skipping error' in caplog.text

def test_setup_logging():
    streaming.setup_logging(logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG

def test_cli_manage_commands():
    runner = CliRunner()
    result = runner.invoke(streaming.cli, ['scaffold', 'test'])
    assert 'Scaffolded strategy test' in result.output
    result = runner.invoke(streaming.cli, ['launch'])
    assert 'Pipeline launched' in result.output
    result = runner.invoke(streaming.cli, ['inspect'])
    assert 'Runtime metrics' in result.output

def test_parallelize_stages():
    @streaming.parallelize_stages
    def f():
        pass
    p = f()
    assert isinstance(p, multiprocessing.Process)
    p.terminate()
    p.join()
