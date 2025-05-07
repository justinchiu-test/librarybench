import zlib

class EncoderConfig:
    def __init__(self, algorithm='none', compression_level=6):
        self.algorithm = algorithm
        self.compression_level = compression_level

    def encode(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        if self.algorithm == 'zlib':
            return zlib.compress(data, self.compression_level)
        elif self.algorithm == 'none':
            return bytes(data)
        else:
            raise ValueError(f"Unsupported algorithm '{self.algorithm}'")

    def decode(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes or bytearray")
        if self.algorithm == 'zlib':
            return zlib.decompress(data)
        elif self.algorithm == 'none':
            return bytes(data)
        else:
            raise ValueError(f"Unsupported algorithm '{self.algorithm}'")

def encoding_configuration(settings: dict):
    """
    Settings can include 'algorithm' (e.g., 'zlib' or 'none')
    and 'compression_level' (0-9 for zlib).
    """
    algorithm = settings.get('algorithm', 'none')
    compression_level = settings.get('compression_level', 6)
    return EncoderConfig(algorithm=algorithm, compression_level=compression_level)
