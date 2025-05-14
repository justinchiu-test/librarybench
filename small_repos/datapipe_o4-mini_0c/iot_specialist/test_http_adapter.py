import pytest
import time
from telemetry.http_adapter import HTTPAdapter

class DummyResp:
    def __init__(self, code):
        self.status_code = code

class DummySession:
    def __init__(self, codes):
        self.codes = codes
        self.calls = 0
    def get(self, url):
        code = self.codes[self.calls]
        self.calls += 1
        return DummyResp(code)
    def post(self, url, data):
        code = self.codes[self.calls]
        self.calls += 1
        return DummyResp(code)

def test_get_success_after_retry():
    session = DummySession([500, 200])
    adapter = HTTPAdapter(session, retries=3, backoff=0)
    resp = adapter.get("http://test")
    assert resp.status_code == 200

def test_get_fail():
    session = DummySession([500, 500, 500])
    adapter = HTTPAdapter(session, retries=2, backoff=0)
    with pytest.raises(Exception):
        adapter.get("http://fail")

def test_post_success():
    session = DummySession([500, 201])
    adapter = HTTPAdapter(session, retries=2, backoff=0)
    resp = adapter.post("http://post", data={'a':1})
    assert resp.status_code == 201

def test_post_fail():
    session = DummySession([500, 500, 500])
    adapter = HTTPAdapter(session, retries=2, backoff=0)
    with pytest.raises(Exception):
        adapter.post("http://fail", data={})
