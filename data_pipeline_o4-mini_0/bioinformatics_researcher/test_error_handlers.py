import pytest
from pipeline.error_handlers import fallback_reads, skip_reads, retry

def test_fallback_reads():
    data = [{'a': 1}]
    out = fallback_reads(data, {})
    assert isinstance(out, list) and out[0]['id'] == 'dummy'

def test_skip_reads():
    reads = [{'mismatches': 5}, {'mismatches': 1}]
    class Met:
        def __init__(self):
            self.skipped_reads = 0
        def inc(self, k, a):
            setattr(self, k, getattr(self, k, 0) + a)
    met = Met()
    kept = skip_reads(reads, threshold=2, context={'metrics': met})
    assert len(kept) == 1
    assert met.skipped_reads == 1

def test_retry_success():
    calls = []
    @retry(max_retries=3, backoff_factor=0)
    def flaky():
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("fail")
        return 'ok'
    assert flaky() == 'ok'
    assert len(calls) == 2

def test_retry_fail():
    @retry(max_retries=1, backoff_factor=0)
    def always_fail():
        raise RuntimeError("bad")
    with pytest.raises(RuntimeError):
        always_fail()
