import pytest
import chaoslib

def test_request_recording():
    chaoslib.startRequestRecording()
    resp1 = chaoslib.httpClient.get("http://service/test1")
    resp2 = chaoslib.httpClient.post("http://service/test2", headers={'X-Test': '1'}, body='data')
    assert len(chaoslib.request_recording) == 2
    first = chaoslib.request_recording[0]
    assert first['method'] == 'GET'
    assert first['url'] == "http://service/test1"
    second = chaoslib.request_recording[1]
    assert second['method'] == 'POST'
    assert second['headers'] == {'X-Test': '1'}
    assert second['body'] == 'data'
    assert resp1.status_code == 200
    assert resp2.status_code == 200
