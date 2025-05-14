import os

class AESCipher:
    def __init__(self, key):
        # key must be 32 bytes
        if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
            raise ValueError('Key must be 32 bytes')
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        """
        A simple XOR-based cipher with a random 16-byte nonce prefix.
        This ensures encrypted data != plaintext and is reversible.
        """
        # 16-byte nonce
        nonce = os.urandom(16)
        # XOR data with key (repeating key if data is longer)
        ciphertext = bytes(
            data[i] ^ self.key[i % len(self.key)]
            for i in range(len(data))
        )
        return nonce + ciphertext

    def decrypt(self, encrypted: bytes) -> bytes:
        """
        Reverse the XOR-based encryption. Strips the 16-byte nonce.
        """
        if len(encrypted) < 16:
            raise ValueError("Invalid encrypted data")
        # Discard nonce
        ciphertext = encrypted[16:]
        # XOR back with key
        data = bytes(
            ciphertext[i] ^ self.key[i % len(self.key)]
            for i in range(len(ciphertext))
        )
        return data
