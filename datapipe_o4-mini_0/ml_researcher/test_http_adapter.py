import pytest
import requests
from feature_pipeline.http_adapter import HTTPAdapter

class DummyResponse:
    def __init__(self, status, json_data):
        self.status_code = status
        self._json = json_data
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")
    def json(self):
        return self._json

def test_http_adapter_retries(monkeypatch):
    calls = []
    def fake_get(url):
        calls.append(url)
        if len(calls) < 3:
            raise requests.RequestException("fail")
        return DummyResponse(200, {"ok": True})
    monkeypatch.setattr(requests, "get", fake_get)
    adapter = HTTPAdapter("http://example.com", retries=3, backoff=0)
    result = adapter.get("/test")
    assert result == {"ok": True}
    assert len(calls) == 3

def test_http_adapter_failure(monkeypatch):
    def fake_get(url):
        raise requests.RequestException("down")
    monkeypatch.setattr(requests, "get", fake_get)
    adapter = HTTPAdapter("http://ex", retries=2, backoff=0)
    with pytest.raises(Exception):
        adapter.get("p")
