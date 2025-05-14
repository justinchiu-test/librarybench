import chaoslib

def handler(method, path, headers, body):
    return chaoslib.Response(status_code=201, body="created", headers={'H': 'V'})

def test_register_and_call_endpoint():
    chaoslib.registerEndpoint('/api/data', handler)
    resp = chaoslib.httpClient.get("http://svc/api/data")
    assert resp.status_code == 201
    assert resp.body == "created"
    assert resp.headers == {'H': 'V'}
