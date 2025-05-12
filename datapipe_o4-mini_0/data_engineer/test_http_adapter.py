import pytest
import urllib.error
from pipeline.http_adapter import HTTPAdapter

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def read(self):
        return self._data
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

def test_get_success(monkeypatch):
    calls = []
    def fake_urlopen(req, timeout):
        assert req.method == 'GET'
        calls.append((req.full_url, timeout))
        return DummyResponse(b"ok")
    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)
    adapter = HTTPAdapter(headers={'h':'v'}, timeout=2, retries=1)
    data = adapter.get('http://example.com')
    assert data == b"ok"
    assert calls == [('http://example.com', 2)]

def test_get_retry(monkeypatch):
    attempts = {'count': 0}
    def fake_urlopen(req, timeout):
        if attempts['count'] == 0:
            attempts['count'] += 1
            raise urllib.error.URLError("error")
        return DummyResponse(b"ok2")
    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)
    adapter = HTTPAdapter(retries=2, retry_delay=0)
    data = adapter.get('url')
    assert data == b"ok2"
    assert attempts['count'] == 1

def test_post_success(monkeypatch):
    def fake_urlopen(req, timeout):
        assert req.method == 'POST'
        return DummyResponse(b"posted")
    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)
    adapter = HTTPAdapter()
    data = adapter.post('u', 'data')
    assert data == b"posted"
