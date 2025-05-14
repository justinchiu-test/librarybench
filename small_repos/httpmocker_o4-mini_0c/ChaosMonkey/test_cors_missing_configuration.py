import chaoslib

def test_options_without_cors():
    # No cors_config set
    resp = chaoslib.httpClient.request('OPTIONS', "http://service/no-cors", headers={'Origin': 'any'})
    # Should not treat as preflight, normal Response
    assert resp.status_code == 200
    assert resp.body == "OK"
