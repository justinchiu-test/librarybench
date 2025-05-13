import pytest
import chaoslib

def test_simulate_5xx_error():
    chaoslib.startRequestRecording()
    # Force 5xx error always, only once
    chaoslib.simulateError('5xx', probability=1.0, times=1)
    with pytest.raises(chaoslib.HTTP5xxError):
        chaoslib.httpClient.get("http://service/error")
    # After one time, no more simulation
    resp = chaoslib.httpClient.get("http://service/error")
    assert resp.status_code == 200

def test_simulate_timeout_and_retry():
    chaoslib.startRequestRecording()
    chaoslib.setRetryPolicy(retries=1, backoff=lambda x: 0)
    # Simulate timeout once
    chaoslib.simulateError('timeout', probability=1.0, times=1)
    resp = chaoslib.httpClient.get("http://service/timeout")
    assert isinstance(resp, chaoslib.Response)
    assert resp.status_code == 200
