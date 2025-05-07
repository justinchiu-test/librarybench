import zlib

def compression_option(data):
    """
    Compress data only if it actually shrinks:
     - str input: if compressing to bytes makes it smaller, return bytes; else return original str.
     - bytes / bytearray input: if compressing makes it smaller, return bytes; else return original (preserving bytes vs. bytearray).
    """
    # String input
    if isinstance(data, str):
        bdata = data.encode('utf-8')
        comp = zlib.compress(bdata)
        # Only keep compressed if smaller
        if len(comp) < len(bdata):
            return comp
        return data

    # Bytes or bytearray input
    if isinstance(data, (bytes, bytearray)):
        bdata = bytes(data)
        comp = zlib.compress(bdata)
        if len(comp) < len(bdata):
            return comp
        # preserve original type
        if isinstance(data, bytearray):
            return bytearray(data)
        return data

    raise TypeError(f"Unsupported type for compression_option: {type(data)}")
