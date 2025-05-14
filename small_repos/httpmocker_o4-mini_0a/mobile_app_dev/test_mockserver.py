import re
import base64
import time
import pytest
from mockserver import MockServer, MockWebSocketConnection

def test_register_and_dispatch_static():
    server = MockServer()
    def handler(req): return "ok"
    server.registerEndpoint('GET', '/test', handler)
    resp = server.dispatch_request('GET', '/test')
    assert resp['status'] == 200
    assert resp['body'] == "ok"

def test_register_and_dispatch_regex():
    server = MockServer()
    def handler(req):
        return {"id": req['path'].split('/')[-1]}
    server.registerEndpoint('GET', re.compile(r'^/user/\d+$'), handler)
    resp = server.dispatch_request('GET', '/user/123')
    assert resp['body'] == {"id": "123"}

def test_assert_header_pass_and_fail():
    server = MockServer()
    def h(req): return "ok"
    server.registerEndpoint('POST', '/h', h).assertHeader('X-Test', 'val')
    # pass
    resp = server.dispatch_request('POST', '/h', headers={'X-Test': 'val'})
    assert resp['body'] == "ok"
    # fail
    with pytest.raises(AssertionError):
        server.dispatch_request('POST', '/h', headers={'X-Test': 'wrong'})

def test_assert_body_predicate_and_schema():
    server = MockServer()
    predicate = lambda b: b.get('x') == 1
    schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}
    def h(req): return "ok"
    server.registerEndpoint('PUT', '/b', h).assertBody(predicate).assertBody(schema)
    # pass
    body = json_body = '{"x":1}'
    resp = server.dispatch_request('PUT', '/b', body=body)
    assert resp['body'] == "ok"
    # predicate fail
    with pytest.raises(AssertionError):
        server.dispatch_request('PUT', '/b', body='{"x":2}')
    # schema fail
    with pytest.raises(AssertionError):
        server.dispatch_request('PUT', '/b', body='{"y":2}')

def test_configure_cors():
    server = MockServer()
    def h(req): return "ok"
    server.registerEndpoint('GET', '/c', h).configureCORS(allowed_origins='*', allowed_methods=['GET'], allowed_headers=['X'])
    pre = server.dispatch_request('OPTIONS', '/c')
    assert pre['status'] == 204
    assert pre['headers']['Access-Control-Allow-Origin'] == '*'
    assert 'GET' in pre['headers']['Access-Control-Allow-Methods']
    resp = server.dispatch_request('GET', '/c')
    assert resp['headers']['Access-Control-Allow-Origin'] == '*'

def test_simulate_basic_and_bearer_auth():
    server = MockServer()
    def h(req): return "ok"
    server.registerEndpoint('GET', '/a', h).simulateAuth('Basic', ('u','p'))
    # fail
    resp = server.dispatch_request('GET', '/a')
    assert resp['status'] == 401
    # pass
    token = base64.b64encode(b"u:p").decode()
    resp = server.dispatch_request('GET', '/a', headers={'Authorization': f"Basic {token}"})
    assert resp['status'] == 200
    # bearer
    server = MockServer()
    server.registerEndpoint('GET', '/b', h).simulateAuth('Bearer', 'tok')
    resp = server.dispatch_request('GET', '/b')
    assert resp['status'] == 401
    resp = server.dispatch_request('GET', '/b', headers={'Authorization': 'Bearer tok'})
    assert resp['status'] == 200

def test_assert_query_param():
    server = MockServer()
    def h(req): return "ok"
    server.registerEndpoint('GET', '/q', h).assertQueryParam('id', re.compile(r'\d+'))
    resp = server.dispatch_request('GET', '/q', query={'id': '123'})
    assert resp['body'] == "ok"
    with pytest.raises(AssertionError):
        server.dispatch_request('GET', '/q', query={'id': 'x'})

def test_rate_limiting():
    server = MockServer()
    def h(req): return "ok"
    server.registerEndpoint('GET', '/r', h).simulateRateLimiting(2, 1)
    # two passes
    assert server.dispatch_request('GET', '/r')['status'] == 200
    assert server.dispatch_request('GET', '/r')['status'] == 200
    # third blocked
    resp = server.dispatch_request('GET', '/r')
    assert resp['status'] == 429
    assert resp['headers']['Retry-After'] == '1'
    # after window
    time.sleep(1.1)
    assert server.dispatch_request('GET', '/r')['status'] == 200

def test_chunked_transfer():
    server = MockServer()
    def h(req): return "ignored"
    chunks = ['a','b','c']
    server.registerEndpoint('GET', '/ch', h).simulateChunkedTransfer(chunks)
    gen = server.dispatch_request('GET', '/ch')
    assert hasattr(gen, '__iter__')
    received = [part['body'] for part in gen]
    assert received == chunks

def test_hot_reload_handlers():
    server = MockServer()
    def h1(req): return "one"
    server.registerEndpoint('GET', '/1', h1)
    assert server.dispatch_request('GET', '/1')['body'] == "one"
    new_defs = [('GET','/2', lambda req: "two")]
    server.hotReloadHandlers(new_defs)
    with pytest.raises(ValueError):
        server.dispatch_request('GET', '/1')
    assert server.dispatch_request('GET', '/2')['body'] == "two"

def test_mock_websocket():
    server = MockServer()
    results = []
    def on_connect(ws):
        # echo one message
        ws.send("hello")
        msg = ws.recv(timeout=1)
        ws.send(f"echo:{msg}")
    server.mockWebSocket('/ws', on_connect)
    conn = server.connect_websocket('/ws')
    # receive initial
    m1 = conn.recv(timeout=1)
    assert m1 == "hello"
    # send and get echo
    conn.send("ping")
    m2 = conn.recv(timeout=1)
    assert m2 == "echo:ping"
