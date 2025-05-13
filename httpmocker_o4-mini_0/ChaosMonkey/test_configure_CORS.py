import chaoslib

def test_cors_allowed():
    chaoslib.configureCORS(
        allow_origins=['http://allowed.com'],
        allow_methods=['GET', 'OPTIONS'],
        allow_headers=['X-Test']
    )
    headers = {'Origin': 'http://allowed.com'}
    resp = chaoslib.httpClient.request('OPTIONS', "http://service/any", headers=headers)
    assert resp.status_code == 200
    assert resp.headers.get('Access-Control-Allow-Origin') == 'http://allowed.com'
    assert 'GET' in resp.headers.get('Access-Control-Allow-Methods', '')

def test_cors_denied():
    chaoslib.configureCORS(
        allow_origins=['http://allowed.com'],
        allow_methods=['GET', 'OPTIONS'],
        allow_headers=['X-Test']
    )
    headers = {'Origin': 'http://denied.com'}
    resp = chaoslib.httpClient.request('OPTIONS', "http://service/any", headers=headers)
    assert resp.status_code == 403
