"""
Module for streaming decoding.
"""

def stream_decode(data_stream, encoding='utf-8'):
    """
    Decode a data stream of byte chunks.

    Args:
        data_stream (iterable): Iterable of bytes-like objects.
        encoding (str): Encoding to use for decoding.

    Yields:
        str: Decoded string chunks.
    """
    for chunk in data_stream:
        if not isinstance(chunk, (bytes, bytearray)):
            raise ValueError('Chunk must be bytes or bytearray')
        yield chunk.decode(encoding)
