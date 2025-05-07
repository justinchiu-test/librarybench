from utils import to_bytes, compress_if_smaller

def compression_option(data):
    try:
        raw = to_bytes(data, name='data')
    except TypeError:
        raise ValueError('Data must be bytes, bytearray, or str')
    return compress_if_smaller(raw)
