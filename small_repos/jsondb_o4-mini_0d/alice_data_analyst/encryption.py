import os

class Encryption:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        # simple XOR-based encryption with random IV
        key = self.key
        iv = os.urandom(len(key))
        ct = bytearray(len(data))
        for i, b in enumerate(data):
            ct[i] = b ^ key[i % len(key)] ^ iv[i % len(iv)]
        return iv + bytes(ct)

    def decrypt(self, data):
        key = self.key
        iv = data[:len(key)]
        ct = data[len(key):]
        pt = bytearray(len(ct))
        for i, b in enumerate(ct):
            pt[i] = b ^ key[i % len(key)] ^ iv[i % len(iv)]
        return bytes(pt)
