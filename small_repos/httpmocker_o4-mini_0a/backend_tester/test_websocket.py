import pytest
import time
from mockserver import MockServer

def test_websocket_echo():
    srv = MockServer()
    def handler(ws):
        msg = ws.receive_loop()
        ws.write(msg + "_echo")
    srv.mockWebSocket('/ws', handler)
    conn = srv.ws_connect('/ws')
    conn.send(b'hello')
    resp = conn.recv(timeout=1)
    assert resp == b'hello_echo'

def test_websocket_no_endpoint():
    srv = MockServer()
    with pytest.raises(ConnectionError):
        srv.ws_connect('/no')
