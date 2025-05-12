import pytest
import requests
from http_adapter import HTTPAdapter

class DummyResponse:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data
    def json(self):
        return self._data

def test_fetch_success(monkeypatch):
    adapter = HTTPAdapter(retries=2, backoff=0)
    calls = []
    def fake_get(url):
        calls.append(url)
        return DummyResponse(200, {"ok": True})
    monkeypatch.setattr(requests, 'get', fake_get)
    resp = adapter.fetch("http://test")
    assert resp == {"ok": True}
    assert calls == ["http://test"]

def test_fetch_retry_and_fail(monkeypatch):
    adapter = HTTPAdapter(retries=2, backoff=0)
    def fake_get(url):
        return DummyResponse(500, {})
    monkeypatch.setattr(requests, 'get', fake_get)
    with pytest.raises(RuntimeError):
        adapter.fetch("http://fail")

def test_submit_success(monkeypatch):
    adapter = HTTPAdapter(retries=1, backoff=0)
    def fake_post(url, json):
        return DummyResponse(200, {"sent": json})
    monkeypatch.setattr(requests, 'post', fake_post)
    data = {"a":1}
    resp = adapter.submit("http://post", data)
    assert resp == {"sent": data}
