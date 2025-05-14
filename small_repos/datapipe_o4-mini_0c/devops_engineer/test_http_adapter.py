import requests
import pytest
from pipeline.http_adapter import HTTPAdapter

class DummyResp:
    def __init__(self, ok):
        self.ok = ok
    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError("fail")

def test_http_adapter_retries(monkeypatch):
    calls = {'count': 0}
    def fake_get(url, json, headers):
        calls['count'] += 1
        return DummyResp(calls['count'] >= 2)
    monkeypatch.setattr(requests, 'get', fake_get)
    adapter = HTTPAdapter(retries=3, backoff=0)
    resp = adapter.get('http://example.com')
    assert resp.ok
    assert calls['count'] == 2

def test_http_adapter_fail(monkeypatch):
    def fake_get(url, json, headers):
        return DummyResp(False)
    monkeypatch.setattr(requests, 'get', fake_get)
    adapter = HTTPAdapter(retries=2, backoff=0)
    with pytest.raises(requests.HTTPError):
        adapter.get('http://example.com')
