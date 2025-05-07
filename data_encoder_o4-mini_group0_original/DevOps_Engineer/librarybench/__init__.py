import zlib

def compression_option(data):
    """
    Compress data with zlib if it makes it smaller; otherwise return the raw bytes.
    Accepts str, bytes, or bytearray. Always returns bytes or bytearray.
    """
    # Normalize to bytes
    if isinstance(data, str):
        raw = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raise TypeError(f"Unsupported type for compression_option: {type(data)}")

    # zlib.compress produces a zlib-wrapped stream (RFC1950),
    # which zlib.decompress() will accept.
    compressed = zlib.compress(raw)

    # Only return the compressed form if it actually shrank
    return compressed if len(compressed) < len(raw) else raw
