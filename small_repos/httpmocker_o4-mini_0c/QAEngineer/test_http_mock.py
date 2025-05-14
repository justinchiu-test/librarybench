import pytest
import re
from mock_server import MockServer, Request, Response
from http_client import HttpClient

def test_request_recording():
    server = MockServer()
    client = HttpClient(server)
    server.startRequestRecording()
    server.registerEndpoint('GET', '/test', lambda req: Response(200, {}, "ok"))
    resp = client.get('/test', headers={'X-A': '1'}, params={'q': 'v'})
    assert resp.status_code == 200
    assert resp.body == "ok"
    assert len(server.requests) == 1
    req = server.requests[0]
    assert req.method == 'GET'
    assert req.path == '/test'
    assert req.headers['X-A'] == '1'
    assert req.params['q'] == 'v'

def test_register_and_dynamic_callback():
    server = MockServer()
    client = HttpClient(server)
    def handler(req):
        return Response(201, {'H':'v'}, {'key': 'val'})
    server.registerEndpoint('POST', '/items', handler)
    # default handler
    resp1 = client.post('/items', headers={}, body={'x':1})
    assert resp1.status_code == 201
    assert resp1.body == {'key':'val'}
    # dynamic callback overrides
    server.addDynamicCallback('POST', '/items', lambda req: Response(202, {}, "dyn"))
    resp2 = client.post('/items', headers={}, body=None)
    assert resp2.status_code == 202
    assert resp2.body == "dyn"

def test_simulate_error_5xx_and_timeout_and_connection():
    server = MockServer()
    client = HttpClient(server)
    server.simulateError('GET', '/e1', '500')
    server.simulateError('GET', '/e2', 'timeout')
    server.simulateError('GET', '/e3', 'connection_reset')
    # 5xx
    resp = client.get('/e1')
    assert resp.status_code == 500
    # timeout
    with pytest.raises(TimeoutError):
        client.get('/e2')
    # connection reset
    with pytest.raises(ConnectionResetError):
        client.get('/e3')

def test_retry_policy():
    server = MockServer()
    client = HttpClient(server)
    calls = {'count': 0}
    def handler(req):
        calls['count'] += 1
        if calls['count'] < 3:
            raise TimeoutError()
        return Response(200, {}, "ok")
    server.registerEndpoint('GET', '/retry', handler)
    client.setRetryPolicy('GET', '/retry', retries=5, backoff=0)
    resp = client.get('/retry')
    assert resp.body == "ok"
    assert calls['count'] == 3

def test_assert_header_and_body():
    server = MockServer()
    def handler(req):
        server.assertHeader(req, 'X-Test')
        server.assertHeader(req, 'X-Num', value=r'\d+', regex=True)
        server.assertRequestBody(req, schema={'a': int, 'b': str})
        server.assertRequestBody(req, predicate=lambda b: b['a'] > 0)
        return Response(200)
    server.registerEndpoint('PUT', '/check', handler)
    client = HttpClient(server)
    headers = {'X-Test': 'yes', 'X-Num': '123'}
    body = {'a': 10, 'b': 'bb'}
    resp = client.put('/check', headers=headers, body=body)
    assert resp.status_code == 200

def test_not_found():
    server = MockServer()
    client = HttpClient(server)
    resp = client.get('/no')
    assert resp.status_code == 404

def test_cors_preflight_and_headers():
    server = MockServer()
    cors = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,POST'}
    server.configureCORS(cors)
    # OPTIONS
    resp = server.handle_request('OPTIONS', '/any')
    assert resp.status_code == 200
    assert resp.headers == cors
    # non-options without endpoint => 404
    r2 = server.handle_request('GET', '/any')
    assert r2.status_code == 404

def test_malformed_response():
    server = MockServer()
    client = HttpClient(server)
    server.simulateError('GET', '/bad', 'malformed')
    resp = client.get('/bad')
    assert resp.body == "<<malformed>>"

def test_query_params_and_headers_reflected():
    server = MockServer()
    def handler(req):
        return Response(200, {'Echo-Param': req.params.get('p', '')}, json.dumps(req.headers))
    server.registerEndpoint('GET', '/echo', handler)
    client = HttpClient(server)
    headers = {'A': 'B'}
    resp = client.get('/echo', headers=headers, params={'p': 'val'})
    assert resp.status_code == 200
    assert resp.headers['Echo-Param'] == 'val'
    # body is JSON of headers
    body = resp.body
    assert '"A": "B"' in body
