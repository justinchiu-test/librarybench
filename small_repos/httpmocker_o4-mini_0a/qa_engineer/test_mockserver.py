import pytest
import re
import base64
import time
from mockserver import (
    MockServer, Request, Response, MockWebSocket,
    assertHeader, assertQueryParam, assertBody,
    simulateAuth, simulateChunkedTransfer
)

def test_register_and_handle_static():
    srv = MockServer()
    def handler(req):
        return Response(200, body='ok')
    srv.registerEndpoint('GET', '/test', handler)
    req = Request('GET', '/test')
    resp = srv.handleRequest(req)
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert resp.body == 'ok'

def test_register_and_handle_regex():
    srv = MockServer()
    def handler(req):
        return Response(201, body=req.path)
    srv.registerEndpoint('GET', r'^/item/\d+$', handler)
    req = Request('GET', '/item/123')
    resp = srv.handleRequest(req)
    assert resp.status_code == 201
    assert resp.body == '/item/123'
    # non-matching
    resp2 = srv.handleRequest(Request('GET', '/item/abc'))
    assert resp2.status_code == 404

def test_assert_header_success_and_failure():
    @assertHeader('X-Test', 'value')
    def h(req):
        return Response(200)
    # success
    req = Request('GET', '/x', headers={'X-Test': 'value'})
    resp = h(req)
    assert resp.status_code == 200
    # missing
    with pytest.raises(AssertionError):
        h(Request('GET', '/x', headers={}))
    # wrong value
    with pytest.raises(AssertionError):
        h(Request('GET', '/x', headers={'X-Test': 'other'}))

def test_assert_query_param():
    @assertQueryParam('q', 'hello')
    def h(req):
        return Response(200)
    req = Request('GET', '/q', query_params={'q': 'hello'})
    assert h(req).status_code == 200
    with pytest.raises(AssertionError):
        h(Request('GET', '/q', query_params={}))

def test_assert_body_schema_and_predicate():
    schema = {'required': ['a', 'b']}
    @assertBody(schema=schema, predicate=lambda d: d['a'] == 1)
    def h(req):
        return Response(200)
    good = Request('POST', '/b', body='{"a":1,"b":2}')
    assert h(good).status_code == 200
    # missing field
    bad1 = Request('POST', '/b', body='{"a":1}')
    with pytest.raises(AssertionError):
        h(bad1)
    # predicate fail
    bad2 = Request('POST', '/b', body='{"a":2,"b":3}')
    with pytest.raises(AssertionError):
        h(bad2)
    # invalid json
    bad3 = Request('POST', '/b', body='notjson')
    with pytest.raises(AssertionError):
        h(bad3)

def test_configure_cors_and_options():
    srv = MockServer()
    srv.configureCORS(allow_origin='http://example.com',
                      allow_methods=['GET','POST'],
                      allow_headers=['X-Custom'])
    # preflight
    req = Request('OPTIONS', '/any')
    resp = srv.handleRequest(req)
    assert resp.status_code == 204
    assert resp.headers['Access-Control-Allow-Origin'] == 'http://example.com'

def test_simulate_basic_auth():
    creds = ['user:pass']
    @simulateAuth('basic', creds)
    def h(req):
        return Response(200, body='ok')
    # missing
    resp1 = h(Request('GET','/', headers={}))
    assert resp1.status_code == 401
    # wrong creds
    token = base64.b64encode(b'user:wrong').decode()
    resp2 = h(Request('GET','/', headers={'Authorization': f'Basic {token}'}))
    assert resp2.status_code == 403
    # good
    token2 = base64.b64encode(b'user:pass').decode()
    resp3 = h(Request('GET','/', headers={'Authorization': f'Basic {token2}'}))
    assert resp3.status_code == 200

def test_simulate_bearer_auth():
    toks = ['secrettoken']
    @simulateAuth('bearer', toks)
    def h(req):
        return Response(200)
    # missing
    r1 = h(Request('GET','/', headers={}))
    assert r1.status_code == 401
    # wrong
    r2 = h(Request('GET','/', headers={'Authorization':'Bearer wrong'}))
    assert r2.status_code == 403
    # good
    r3 = h(Request('GET','/', headers={'Authorization':'Bearer secrettoken'}))
    assert r3.status_code == 200

def test_rate_limiting():
    srv = MockServer()
    def h(req): return Response(200)
    srv.registerEndpoint('GET','/rl', h)
    srv.simulateRateLimiting('u1', limit=2, window=1)
    # first two ok
    req = Request('GET','/rl', headers={'X-RateLimit-User':'u1'})
    assert srv.handleRequest(req).status_code == 200
    assert srv.handleRequest(req).status_code == 200
    # third is 429
    r = srv.handleRequest(req)
    assert isinstance(r, Response)
    assert r.status_code == 429
    assert 'Retry-After' in r.headers
    # after window reset
    time.sleep(1.1)
    r2 = srv.handleRequest(req)
    assert r2.status_code == 200

def test_chunked_transfer():
    @simulateChunkedTransfer(lambda b: (c for c in [b[:2], b[2:]]))
    def h(req):
        return Response(200, body='abcd')
    srv = MockServer()
    srv.registerEndpoint('GET','/c', h)
    req = Request('GET','/c')
    resp = srv.handleRequest(req)
    assert resp.status_code == 200
    assert resp.headers.get('Transfer-Encoding') == 'chunked'
    chunks = list(resp.body)
    assert chunks == ['ab','cd']

def test_hot_reload_handlers():
    srv = MockServer()
    srv.registerEndpoint('GET','/a', lambda r: Response(200, body='a'))
    srv.hotReloadHandlers([('GET','/b', lambda r: Response(200, body='b'))])
    r1 = srv.handleRequest(Request('GET','/a'))
    assert r1.status_code == 404
    r2 = srv.handleRequest(Request('GET','/b'))
    assert r2.body == 'b'

def test_mock_websocket():
    srv = MockServer()
    def ws_handler(ws):
        ws.send('hello')
        return ws
    srv.mockWebSocket('/ws', ws_handler)
    result = srv.handleRequest(Request('GET','/ws'))
    assert isinstance(result, MockWebSocket)
    assert result.receive() == 'hello'
    # simulate error
    result.simulateError(RuntimeError('fail'))
    with pytest.raises(RuntimeError):
        result.send('x')
