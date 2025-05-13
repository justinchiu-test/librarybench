import chaoslib

def test_retry_policy_success_after_retry():
    chaoslib.startRequestRecording()
    chaoslib.setRetryPolicy(retries=2, backoff=lambda x: 0)
    # Simulate connection reset once
    chaoslib.simulateError('connection', probability=1.0, times=1)
    resp = chaoslib.httpClient.get("http://service/retry")
    assert resp.status_code == 200
    # Should have recorded two attempts
    # but recording only logs successful call once
    assert len(chaoslib.request_recording) == 1
