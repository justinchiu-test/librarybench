import base64
from typing import Iterable, Generator, Union, Dict

# Module-level global security configuration
_GLOBAL_CONFIG: Dict[str, Union[bytes, int]] = {
    'key': b'default_key',
    'level': 1
}


def configure_security(settings: Dict[str, Union[str, bytes, int]]) -> Dict[str, Union[bytes, int]]:
    """
    Configure global security settings.
    settings must include:
      - 'key': encryption key (str or bytes)
      - 'level': number of XOR rounds (int >= 1)
    Returns the updated configuration.
    """
    if 'key' not in settings or 'level' not in settings:
        raise KeyError("Both 'key' and 'level' must be provided in settings.")
    key = settings['key']
    if isinstance(key, str):
        key = key.encode('utf-8')
    if not isinstance(key, (bytes, bytearray)) or len(key) == 0:
        raise ValueError("'key' must be a non-empty bytes or string.")
    level = settings['level']
    if not isinstance(level, int) or level < 1:
        raise ValueError("'level' must be an integer >= 1.")
    _GLOBAL_CONFIG['key'] = key
    _GLOBAL_CONFIG['level'] = level
    # Return a copy to avoid external mutation
    return {'key': _GLOBAL_CONFIG['key'], 'level': _GLOBAL_CONFIG['level']}


def _xor_cipher(data: bytes, key: bytes) -> bytes:
    """
    Single-round XOR cipher.
    """
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _encrypt_bytes(data: bytes, key: bytes, level: int) -> bytes:
    """
    Apply XOR cipher 'level' times.
    """
    result = data
    for _ in range(level):
        result = _xor_cipher(result, key)
    return result


def encode(data: Union[str, bytes], config: Dict[str, Union[bytes, int]]) -> str:
    """
    Encode (encrypt + base64) the input data using provided config.
    Returns a string with version prefix "v1:".
    """
    if 'key' not in config or 'level' not in config:
        raise KeyError("Config must contain 'key' and 'level'.")
    key = config['key']
    level = config['level']
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        data_bytes = bytes(data)
    else:
        raise TypeError("Data must be str or bytes.")
    encrypted = _encrypt_bytes(data_bytes, key, level)
    b64 = base64.b64encode(encrypted).decode('utf-8')
    return f"v1:{b64}"


def decode(encoded_data: Union[str, bytes]) -> str:
    """
    Decode the given encoded_data string.
    Supports:
      - v1: encrypted with XOR + base64
      - v0: plain base64 without encryption (no prefix)
    Always returns a string. UTF-8 is attempted first; on failure, falls back to Latin-1.
    """
    # Normalize to string
    if isinstance(encoded_data, bytes):
        encoded_str = encoded_data.decode('utf-8')
    else:
        encoded_str = encoded_data

    def _decode_bytes_to_str(b: bytes) -> str:
        try:
            return b.decode('utf-8')
        except UnicodeDecodeError:
            return b.decode('latin-1')

    if encoded_str.startswith("v1:"):
        # Version 1: encrypted then base64
        b64 = encoded_str[3:]
        encrypted = base64.b64decode(b64)
        key = _GLOBAL_CONFIG['key']
        level = _GLOBAL_CONFIG['level']
        decrypted = _encrypt_bytes(encrypted, key, level)
        return _decode_bytes_to_str(decrypted)
    else:
        # Version 0 backward compatibility: plain base64
        decoded_bytes = base64.b64decode(encoded_str)
        return _decode_bytes_to_str(decoded_bytes)


def stream_encode(data_stream: Iterable[Union[str, bytes]]
                  ) -> Generator[str, None, None]:
    """
    Encode each chunk in the data_stream using the current global config.
    Yields encoded string chunks (including "v1:" prefix for each chunk).
    """
    config = {'key': _GLOBAL_CONFIG['key'], 'level': _GLOBAL_CONFIG['level']}
    for chunk in data_stream:
        yield encode(chunk, config)
