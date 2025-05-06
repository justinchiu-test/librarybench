import json
import gzip
import io

def encode_data(data):
    """
    Serialize a Python object to a JSON-formatted bytestring.
    """
    try:
        # Use compact separators for consistent, minimal JSON output
        text = json.dumps(data, separators=(',',':'))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Unable to JSON-encode data: {e}")
    return text.encode('utf-8')

def compress_data(data_bytes):
    """
    Compress a bytestring using GZIP.
    """
    if not isinstance(data_bytes, (bytes, bytearray)):
        raise TypeError("compress_data expects a bytes-like object")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
        gz.write(data_bytes)
    return buf.getvalue()

def decode_data(compressed_bytes):
    """
    Decompress a GZIP-compressed bytestring and parse the JSON inside,
    returning the original Python object.
    """
    if not isinstance(compressed_bytes, (bytes, bytearray)):
        raise TypeError("decode_data expects a bytes-like GZIP-compressed object")
    buf = io.BytesIO(compressed_bytes)
    with gzip.GzipFile(fileobj=buf, mode='rb') as gz:
        decompressed = gz.read()
    try:
        return json.loads(decompressed.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Unable to decode JSON data: {e}")

def integration_test(data):
    """
    End-to-end pipeline: encode -> compress -> decompress+decode.
    Returns the reconstructed Python object for comparison.
    """
    encoded = encode_data(data)
    compressed = compress_data(encoded)
    return decode_data(compressed)
