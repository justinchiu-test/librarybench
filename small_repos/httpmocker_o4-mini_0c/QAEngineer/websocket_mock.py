from typing import Callable, List

class MockWebSocketServer:
    def __init__(self):
        self.on_handshake = None  # type: Callable[[dict], None]
        self.on_message = None    # type: Callable[[str], None]
        self.on_close = None      # type: Callable[[], None]
        self.messages = []        # type: List[str]
        self.open = True

    def handshake(self, headers: dict):
        if self.on_handshake:
            self.on_handshake(headers)

    def send(self, msg: str):
        if not self.open:
            raise ConnectionResetError("Connection closed")
        self.messages.append(msg)
        if self.on_message:
            self.on_message(msg)

    def close(self):
        self.open = False
        if self.on_close:
            self.on_close()
