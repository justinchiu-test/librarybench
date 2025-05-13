import pytest
import json
import chaoslib

def test_websocket_drop_all():
    srv = chaoslib.mockWebSocket(drop_rate=1.0, malformed_rate=0.0)
    conn = srv.connect()
    msg = conn.receive()
    assert msg is None

def test_websocket_malformed_all():
    srv = chaoslib.mockWebSocket(drop_rate=0.0, malformed_rate=1.0)
    conn = srv.connect()
    msg = conn.receive()
    # Should be a string that is not valid JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(msg)

def test_websocket_valid():
    srv = chaoslib.mockWebSocket(drop_rate=0.0, malformed_rate=0.0)
    conn = srv.connect()
    msg = conn.receive()
    data = json.loads(msg)
    assert data.get('message') == 'hello'
