import zlib

def compression_option(data):
    """
    Take bytes, bytearray, memoryview or str and return either
    - a zlib-compressed bytes object (using zlib.compress), if that
      actually shrinks the payload, or
    - the original bytes (or UTF-8 encoding, for str) if not.

    Other data types are passed through unchanged.
    """
    # Normalize input to raw bytes
    if isinstance(data, (bytes, bytearray, memoryview)):
        raw = bytes(data)
    elif isinstance(data, str):
        raw = data.encode('utf-8')
    else:
        # No compression for other types
        return data

    # Use zlib’s default wrapper (so that zlib.decompress() will succeed)
    compressed = zlib.compress(raw)
    # Only keep compression if it actually helps
    if len(compressed) < len(raw):
        return compressed
    else:
        return raw
