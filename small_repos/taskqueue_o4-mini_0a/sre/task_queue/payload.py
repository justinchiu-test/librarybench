class Payload:
    def __init__(self, descriptor: dict, binary: bytes = b''):
        self.descriptor = descriptor
        self.binary = binary
