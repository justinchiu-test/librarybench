"""
Module for compression options.
"""
import zlib

def compression_option(data):
    """
    Compress data using zlib if beneficial.

    Args:
        data (bytes or str): Data to compress.

    Returns:
        bytes: Compressed data if size is smaller, else original data as bytes.
    """
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        data_bytes = bytes(data)
    else:
        raise ValueError('Data must be bytes, bytearray, or str')

    compressed = zlib.compress(data_bytes)
    # Return compressed if smaller
    if len(compressed) < len(data_bytes):
        return compressed
    return data_bytes
