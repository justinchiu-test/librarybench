import pytest
import re
from mockserver import MockServer, HttpClient, Response

def test_register_and_get_static_endpoint():
    server = MockServer()
    client = HttpClient(server)
    server.registerEndpoint('GET', '/hello', (200, {'Content-Type': 'text'}, 'world'))
    resp = client.get('/hello')
    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text'
    assert resp.body == 'world'

def test_not_found_endpoint():
    server = MockServer()
    client = HttpClient(server)
    resp = client.get('/nope')
    assert resp.status_code == 404
    assert resp.body == 'Not Found'

def test_start_request_recording():
    server = MockServer()
    server.startRequestRecording()
    client = HttpClient(server)
    client.get('/x', headers={'A': '1'})
    client.post('/y', body={'foo': 'bar'})
    assert len(server.recorded_requests) == 2
    assert server.recorded_requests[0]['method'] == 'GET'
    assert server.recorded_requests[1]['method'] == 'POST'

def test_simulate_error_overrides_static():
    server = MockServer()
    client = HttpClient(server)
    server.registerEndpoint('GET', '/err', (200, {}, 'ok'))
    server.simulateError('GET', '/err', 429)
    resp = client.get('/err')
    assert resp.status_code == 429
    assert 'Error 429' in resp.body

def test_assert_header_missing_and_present():
    server = MockServer()
    client = HttpClient(server)
    server.registerEndpoint('GET', '/hdr', (200, {}, 'ok'))
    server.assertHeader('GET', '/hdr', {'X-Api-Key': None})
    # missing
    resp = client.get('/hdr')
    assert resp.status_code == 400
    # present
    resp = client.get('/hdr', headers={'X-Api-Key': 'secret'})
    assert resp.status_code == 200
    assert resp.body == 'ok'

def test_assert_request_body_validator():
    server = MockServer()
    client = HttpClient(server)
    def validator(body):
        return isinstance(body, dict) and 'foo' in body
    server.registerEndpoint('POST', '/data', (200, {}, 'ok'))
    server.assertRequestBody('POST', '/data', validator)
    resp = client.post('/data', body={'nope': 1})
    assert resp.status_code == 400
    resp = client.post('/data', body={'foo': 2})
    assert resp.status_code == 200

def test_dynamic_callback_simple():
    server = MockServer()
    client = HttpClient(server)
    def cb(req):
        return (201, {'X': 'Y'}, f"Got {req['body']}")
    server.addDynamicCallback('POST', '/dyn', cb)
    resp = client.post('/dyn', body='test')
    assert resp.status_code == 201
    assert resp.headers['X'] == 'Y'
    assert resp.body == 'Got test'

def test_dynamic_callback_exception():
    server = MockServer()
    client = HttpClient(server)
    def cb(req):
        raise ValueError("fail")
    server.addDynamicCallback('GET', '/bad', cb)
    resp = client.get('/bad')
    assert resp.status_code == 500
    assert 'fail' in resp.body

def test_regex_endpoint_matching():
    server = MockServer()
    client = HttpClient(server)
    pattern = re.compile(r'/items/\d+')
    server.registerEndpoint('GET', pattern, (200, {}, 'num'))
    resp = client.get('/items/123')
    assert resp.status_code == 200
    assert resp.body == 'num'
    resp2 = client.get('/items/abc')
    assert resp2.status_code == 404

def test_configure_cors_and_access():
    server = MockServer()
    opts = {'origins': ['*'], 'methods': ['GET'], 'headers': ['X'], 'credentials': True}
    server.configureCORS(**opts)
    assert server.cors_options == opts

def test_mock_websocket_registration():
    server = MockServer()
    def handler(msg):
        return f"echo {msg}"
    server.mockWebSocket('/ws', handler)
    assert '/ws' in server.ws_handlers
    assert server.ws_handlers['/ws']('hello') == 'echo hello'

def test_set_retry_policy_storage():
    server = MockServer()
    policy = {'retries': 3, 'backoff': 0.1}
    server.setRetryPolicy(policy)
    assert server.retry_policy == policy
