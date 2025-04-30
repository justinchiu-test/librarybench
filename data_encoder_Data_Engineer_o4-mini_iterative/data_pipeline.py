import json
import zlib
import hashlib
import base64


class DataPipeline:
    """
    A class to handle encoding and decoding of data with optional compression.
    """

    def __init__(self, compression_level: int = 0):
        """
        Initialize the pipeline with a given zlib compression level (0-9).
        0 means no compression.
        """
        if not isinstance(compression_level, int) or not (0 <= compression_level <= 9):
            raise ValueError("compression_level must be an integer between 0 and 9")
        self.compression_level = compression_level

    def encode(self, data) -> bytes:
        """
        Encode a Python data structure to JSON bytes, optionally compressed.
        Raises ValueError if data is not JSON-serializable.
        """
        try:
            # sort_keys for reproducible order, compact separators
            json_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Data not serializable: {e}")

        if self.compression_level > 0:
            try:
                compressed = zlib.compress(json_bytes, level=self.compression_level)
                # wrap compressed bytes in base64 so that they are valid UTF-8 text
                return base64.b64encode(compressed)
            except Exception as e:
                raise ValueError(f"Compression error: {e}")
        else:
            return json_bytes

    def decode(self, data_bytes: bytes):
        """
        Decode bytes (possibly compressed) back to Python data.
        Raises ValueError on malformed input.
        """
        if not isinstance(data_bytes, (bytes, bytearray)):
            raise ValueError("Input must be bytes or bytearray")

        # First, handle optional base64 + decompression
        try:
            if self.compression_level > 0:
                try:
                    compressed = base64.b64decode(data_bytes)
                except Exception as e:
                    raise ValueError(f"Base64 decode error: {e}")
                decompressed = zlib.decompress(compressed)
            else:
                decompressed = data_bytes
        except zlib.error as e:
            raise ValueError(f"Decompression error: {e}")

        try:
            return json.loads(decompressed.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"JSON decode error: {e}")


def data_integrity_checks(data) -> bool:
    """
    Perform an encode-decode cycle with default settings
    and return True if the round-trip preserves the data exactly.
    """
    pipeline = DataPipeline()
    encoded = pipeline.encode(data)
    decoded = pipeline.decode(encoded)
    return decoded == data


def nested_structures(data):
    """
    Encode and decode nested structures to ensure support for nesting.
    Returns the decoded result (should match input).
    """
    pipeline = DataPipeline()
    encoded = pipeline.encode(data)
    return pipeline.decode(encoded)


def streaming_support(data_stream):
    """
    Given an iterable of data items, yields each item encoded (bytes).
    Users can decode each chunk with DataPipeline.decode().
    """
    pipeline = DataPipeline()
    for item in data_stream:
        yield pipeline.encode(item)


def encoding_configuration(settings: dict) -> DataPipeline:
    """
    Construct a DataPipeline according to the given settings dictionary.
    Recognized setting: 'compression_level' (0-9).
    """
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a dict")
    compression_level = settings.get("compression_level", 0)
    return DataPipeline(compression_level=compression_level)
