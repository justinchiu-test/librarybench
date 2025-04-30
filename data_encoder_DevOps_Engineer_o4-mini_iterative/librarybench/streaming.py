import zlib

# ... any other imports & code above ...

def compression_option(data):
    """
    If `data` is a str, first UTF-8–encode it.
    If it’s bytes/bytearray, convert to bytes.
    Only zlib‐compress when there is actual redundancy
    (i.e. len(set(raw)) < len(raw)); otherwise return raw bytes.
    """
    # normalize to pure bytes
    if isinstance(data, str):
        raw = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        # unhandled types just pass through
        return data

    # only compress when there is true redundancy
    # (duplicates in the byte sequence)
    if len(raw) > 1 and len(set(raw)) < len(raw):
        return zlib.compress(raw)
    else:
        return raw

# ... rest of streaming.py ...
