import base64
from typing import Iterable, Generator, Union, Dict
from utils import to_bytes, to_str_fallback, require_keys

# Module-level global security configuration
_GLOBAL_CONFIG: Dict[str, Union[bytes, int]] = {
    'key': b'default_key',
    'level': 1
}

def configure_security(settings: Dict[str, Union[str, bytes, int]]
                       ) -> Dict[str, Union[bytes, int]]:
    require_keys(settings, ['key', 'level'])
    key = to_bytes(settings['key'], name='key')
    if not key:
        raise ValueError("'key' must be a non-empty bytes or string.")
    level = settings['level']
    if not isinstance(level, int) or level < 1:
        raise ValueError("'level' must be an integer >= 1.")
    _GLOBAL_CONFIG['key'] = key
    _GLOBAL_CONFIG['level'] = level
    return {'key': key, 'level': level}

def _xor_cipher(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def _encrypt_bytes(data: bytes, key: bytes, level: int) -> bytes:
    result = data
    for _ in range(level):
        result = _xor_cipher(result, key)
    return result

def encode(data: Union[str, bytes], config: Dict[str, Union[bytes, int]]) -> str:
    require_keys(config, ['key', 'level'])
    if isinstance(data, (str, bytes, bytearray)):
        data_bytes = to_bytes(data, name='data')
    else:
        raise TypeError("Data must be str or bytes.")
    key = config['key']
    level = config['level']
    encrypted = _encrypt_bytes(data_bytes, key, level)
    b64 = base64.b64encode(encrypted).decode('utf-8')
    return f"v1:{b64}"

def decode(encoded_data: Union[str, bytes]) -> str:
    if isinstance(encoded_data, bytes):
        s = encoded_data.decode('utf-8')
    else:
        s = encoded_data
    if s.startswith("v1:"):
        raw = base64.b64decode(s[3:])
        dec = _encrypt_bytes(raw,
                             _GLOBAL_CONFIG['key'],
                             _GLOBAL_CONFIG['level'])
        return to_str_fallback(dec)
    # backward compatibility (v0)
    raw = base64.b64decode(s)
    return to_str_fallback(raw)

def stream_encode(data_stream: Iterable[Union[str, bytes]]
                  ) -> Generator[str, None, None]:
    config = {'key': _GLOBAL_CONFIG['key'], 'level': _GLOBAL_CONFIG['level']}
    for chunk in data_stream:
        yield encode(chunk, config)
