import pytest
import base64
import re
import time
from mockserver import MockServer, MockWebSocketClient

def test_register_and_handle():
    server = MockServer()
    server.registerEndpoint('GET', '/test', lambda req: 'ok')
    resp = server.handle_request('GET', '/test')
    assert resp.status_code == 200
    assert resp.body == 'ok'

def test_hot_reload():
    server = MockServer()
    server.registerEndpoint('GET', '/path', lambda req: 'v1')
    resp1 = server.handle_request('GET', '/path')
    assert resp1.body == 'v1'
    server.registerEndpoint('GET', '/path', lambda req: 'v2')
    resp2 = server.handle_request('GET', '/path')
    assert resp2.body == 'v2'

def test_assert_header_and_query():
    server = MockServer()
    def handler(req):
        server.assertHeader(req, 'X', 'val')
        server.assertHeader(req, 'X2', lambda v: v.startswith('pre'))
        server.assertQueryParam(req, 'q', '1')
        server.assertQueryParam(req, 'r', re.compile(r'\d+'))
        return 'ok'
    server.registerEndpoint('POST', '/h?query', handler)
    headers = {'X': 'val', 'X2': 'pre123'}
    resp = server.handle_request('POST', '/h?query', headers=headers)
    assert resp.status_code == 200

def test_assert_body_schema_and_predicate():
    server = MockServer()
    def handler(req):
        server.assertBody(req, {'a': int, 'b': str})
        server.assertBody(req, lambda d: d.get('a') == 1)
        return 'ok'
    server.registerEndpoint('PUT', '/body', handler)
    body = '{"a":1,"b":"two"}'
    resp = server.handle_request('PUT', '/body', headers={'Content-Type': 'application/json'}, body=body)
    assert resp.status_code == 200

def test_configure_cors():
    server = MockServer()
    server.configureCORS('/cors', headers=['X-Test'])
    resp = server.handle_request('OPTIONS', '/cors')
    assert resp.status_code == 204
    assert resp.headers['Access-Control-Allow-Origin'] == '*'
    assert 'X-Test' in resp.headers['Access-Control-Allow-Headers']

def test_simulate_auth_basic_and_bearer():
    server = MockServer()
    def basic_verifier(token):
        return token == base64.b64encode(b'user:pass').decode()
    server.registerEndpoint('GET', '/secure', lambda req: 'secret')
    server.simulateAuth('GET', '/secure', 'Basic', basic_verifier)
    auth_header = 'Basic ' + base64.b64encode(b'user:pass').decode()
    resp_ok = server.handle_request('GET', '/secure', headers={'Authorization': auth_header})
    assert resp_ok.status_code == 200
    resp_fail = server.handle_request('GET', '/secure')
    assert resp_fail.status_code == 401
    def bearer_verifier(token):
        return token == 'token123'
    server.registerEndpoint('POST', '/bearer', lambda req: 'okb')
    server.simulateAuth('POST', '/bearer', 'Bearer', bearer_verifier)
    resp2 = server.handle_request('POST', '/bearer', headers={'Authorization': 'Bearer token123'})
    assert resp2.status_code == 200
    resp3 = server.handle_request('POST', '/bearer', headers={'Authorization': 'Bearer wrong'})
    assert resp3.status_code == 401

def test_simulate_rate_limiting():
    server = MockServer()
    server.registerEndpoint('GET', '/rate', lambda req: 'r')
    server.simulateRateLimiting('GET', '/rate', 2, 1)
    r1 = server.handle_request('GET', '/rate')
    r2 = server.handle_request('GET', '/rate')
    assert r1.status_code == 200
    assert r2.status_code == 200
    r3 = server.handle_request('GET', '/rate')
    assert r3.status_code == 429
    assert 'Retry-After' in r3.headers
    time.sleep(1)
    r4 = server.handle_request('GET', '/rate')
    assert r4.status_code == 200

def test_simulate_chunked_transfer():
    server = MockServer()
    def handler(req):
        return ['a', 'b', 'c']
    server.registerEndpoint('GET', '/stream', handler)
    resp = server.handle_request('GET', '/stream')
    assert resp.chunks == ['a', 'b', 'c']
    assert resp.status_code == 200

def test_mock_websocket_echo():
    server = MockServer()
    def ws_handler(client):
        start = time.time()
        while time.time() - start < 1:
            if client.outbox:
                msg = client.outbox.pop(0)
                client.inbox.append(msg)
                break
            time.sleep(0.01)
    server.mockWebSocket('/ws', ws_handler)
    client = server.connect_websocket('/ws')
    client.send('hello')
    resp = client.receive(timeout=1)
    assert resp == 'hello'
