import pytest
import time
from mock_env import (
    startRequestRecording, httpClient, simulateError, assertHeader,
    registerEndpoint, configureCORS, mockWebSocket, setRetryPolicy,
    addDynamicCallback, assertRequestBody, HTTPError, WSConnectionError,
    WSDisconnectError, http_record, ws_record
)

def test_register_and_http_request():
    startRequestRecording()
    def auth_handler(req):
        return 200, {'Content-Type': 'application/json'}, {'token': 'abc123'}
    registerEndpoint('GET', '/auth', auth_handler)
    res = httpClient.get('/auth', headers={'Accept': 'application/json'})
    assert res['status'] == 200
    assert res['body']['token'] == 'abc123'
    # Recorded
    assert len(http_record) == 1
    req = http_record[0]
    assert req.method == 'GET' and req.path == '/auth'

def test_simulate_http_error_and_retry_policy():
    startRequestRecording()
    setRetryPolicy(retries=2, backoff=0)
    # Handler never called due to error
    def dummy(req):
        return 200, {}, 'ok'
    registerEndpoint('GET', '/fail', dummy)
    simulateError('http', {'status_code': 502, 'times': 2})
    with pytest.raises(HTTPError) as exc:
        httpClient.get('/fail')
    assert exc.value.status_code == 502
    # Next call succeeds
    res = httpClient.get('/fail')
    assert res['body'] == 'ok'

def test_assert_header_success_and_failure():
    from mock_env import HTTPRequest
    req = HTTPRequest('GET', '/test', headers={'Auth': 'token'})
    # Success
    assertHeader(req, 'Auth', 'token')
    # Missing
    with pytest.raises(AssertionError):
        assertHeader(req, 'Missing')
    # Wrong value
    with pytest.raises(AssertionError):
        assertHeader(req, 'Auth', 'wrong')

def test_configure_cors():
    startRequestRecording()
    def handler(req):
        return 200, {}, 'ok'
    registerEndpoint('GET', '/cors', handler)
    configureCORS(origins=['http://example.com'], headers=['X-Custom'])
    res = httpClient.get('/cors', headers={'Origin': 'http://example.com'})
    assert res['headers']['Access-Control-Allow-Origin'] == 'http://example.com'
    assert 'X-Custom' in res['headers']['Access-Control-Allow-Headers']

def test_assert_request_body():
    from mock_env import HTTPRequest
    req = HTTPRequest('POST', '/data', body={'x': 1})
    # validator returns True
    assertRequestBody(req, lambda b: 'x' in b)
    # validator returns False
    with pytest.raises(AssertionError):
        assertRequestBody(req, lambda b: False)

def test_mock_websocket_basic():
    startRequestRecording()
    # Two clients on same channel
    ws1 = mockWebSocket('game1', headers={'Protocol': 'custom'})
    ws2 = mockWebSocket('game1', headers={'Protocol': 'custom'})
    # Check handshake recorded
    assert len(ws_record) == 2
    # Send message from ws1
    ws1.send({'move': 'A2'})
    msgs = ws2.receive()
    assert msgs and msgs[0]['message'] == {'move': 'A2'}
    # Ping
    assert ws1.ping() == 'pong'
    # Disconnect
    ws1.disconnect()
    assert not ws1.connected

def test_simulate_ws_disconnect_and_reconnect_policy():
    startRequestRecording()
    setRetryPolicy(retries=1, backoff=0)
    # Simulate connect failures
    simulateError('ws', {'connect_failures': 1})
    # First attempt fails, second succeeds
    ws = mockWebSocket('channel2')
    assert ws.connected

def test_ws_dynamic_callback():
    startRequestRecording()
    # Dynamic response echoes with suffix
    def bot(msg):
        if msg.get('chat'):
            return {'chat': msg['chat'] + '!!!'}
    addDynamicCallback('chat1', bot)
    ws = mockWebSocket('chat1')
    ws.send({'chat': 'hello'})
    responses = ws.receive()
    # bot response
    assert any(r['message'] == {'chat': 'hello!!!'} for r in responses)

def test_ws_mid_stream_disconnect():
    startRequestRecording()
    ws_errors = simulateError('ws', {'disconnect_after': 1})
    ws = mockWebSocket('c1')
    # First send ok
    ws.send('msg1')
    # Second send should disconnect
    with pytest.raises(WSDisconnectError):
        ws.send('msg2')

def test_http_not_found():
    startRequestRecording()
    with pytest.raises(HTTPError) as exc:
        httpClient.get('/nope')
    assert exc.value.status_code == 404
