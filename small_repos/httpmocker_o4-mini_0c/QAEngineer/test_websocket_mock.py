import pytest
from websocket_mock import MockWebSocketServer

def test_handshake_and_message_and_close():
    ws = MockWebSocketServer()
    events = []
    ws.on_handshake = lambda headers: events.append(('hs', headers))
    ws.on_message = lambda msg: events.append(('msg', msg))
    ws.on_close = lambda: events.append(('close', None))
    # handshake
    headers = {'Sec-WebSocket-Key': 'abc'}
    ws.handshake(headers)
    # send messages
    ws.send("hello")
    ws.send("world")
    # close
    ws.close()
    assert events[0] == ('hs', headers)
    assert ('msg', 'hello') in events
    assert ('msg', 'world') in events
    assert events[-1] == ('close', None)
    # sending after close raises
    with pytest.raises(ConnectionResetError):
        ws.send("oops")
