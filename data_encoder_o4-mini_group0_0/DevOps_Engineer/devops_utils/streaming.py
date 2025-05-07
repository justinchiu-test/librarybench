from utils import ensure_bytes

def stream_decode(data_stream, encoding='utf-8'):
    for chunk in data_stream:
        raw = ensure_bytes(chunk, name='Chunk')
        yield raw.decode(encoding)
