import zlib

def configure_encoding(settings):
    """
    Configure encoding settings.
    
    Parameters:
      settings (dict): A dictionary of settings. Supported keys:
        - version (int): Encoding version (1 or 2). Version 1 = raw bytes, 
                         Version 2 = zlib compression.
        - compression_level (int): zlib compression level (0-9). Only used in version 2.
    
    Returns:
      dict: A configuration dictionary with keys 'version' and 'compression_level'.
    
    Raises:
      TypeError: If settings is not a dict.
      ValueError: If version or compression_level are out of allowed ranges.
    """
    if not isinstance(settings, dict):
        raise TypeError("settings must be a dict")
    # Defaults
    version = settings.get('version', 2)
    compression_level = settings.get('compression_level', 6)
    # Validation
    if not isinstance(version, int) or version not in (1, 2):
        raise ValueError("version must be 1 or 2")
    if not isinstance(compression_level, int) or not (0 <= compression_level <= 9):
        raise ValueError("compression_level must be an integer between 0 and 9")
    # For version 1, compression_level is irrelevant but we still store it
    return {'version': version, 'compression_level': compression_level}


def encode(data, config):
    """
    Encode data according to the given configuration.
    
    Format:
      [1 byte version][payload]
    
    Version 1: payload = raw bytes of data.
    Version 2: payload = zlib.compress(raw bytes, level=compression_level).
    
    Parameters:
      data (bytes or str): The data to encode.
      config (dict): Configuration dict from configure_encoding().
    
    Returns:
      bytes: The encoded byte string.
    
    Raises:
      TypeError: If data is not bytes or str, or config is not dict.
      ValueError: If config contains invalid values.
    """
    if not isinstance(config, dict):
        raise TypeError("config must be a dict from configure_encoding()")
    # Validate config again
    version = config.get('version')
    compression_level = config.get('compression_level')
    if version not in (1, 2):
        raise ValueError("config['version'] must be 1 or 2")
    if not isinstance(compression_level, int) or not (0 <= compression_level <= 9):
        raise ValueError("config['compression_level'] must be int between 0 and 9")
    # Prepare raw bytes
    if isinstance(data, str):
        raw = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raise TypeError("data must be bytes or str")
    # Encode
    if version == 1:
        payload = raw
    else:
        payload = zlib.compress(raw, level=compression_level)
    return bytes([version]) + payload


def decode(encoded_data):
    """
    Decode data previously encoded with encode().
    
    Parameters:
      encoded_data (bytes or bytearray): Data returned by encode().
    
    Returns:
      bytes: The original raw data bytes.
    
    Raises:
      TypeError: If encoded_data is not bytes-like.
      ValueError: If the version byte is unknown or decompression fails.
    """
    if not isinstance(encoded_data, (bytes, bytearray)):
        raise TypeError("encoded_data must be bytes or bytearray")
    if len(encoded_data) < 1:
        raise ValueError("encoded_data is too short to contain version header")
    version = encoded_data[0]
    payload = bytes(encoded_data[1:])
    if version == 1:
        return payload
    elif version == 2:
        try:
            return zlib.decompress(payload)
        except zlib.error as e:
            raise ValueError(f"decompression failed: {e}")
    else:
        raise ValueError(f"Unknown version: {version}")


def document_api():
    """
    Return comprehensive API documentation for the encoding module.
    
    Returns:
      str: A Markdown-formatted documentation string.
    """
    doc = []
    doc.append("# API Documentation")
    doc.append("")
    doc.append("## configure_encoding(settings)")
    doc.append("Configure encoding settings for the encode function.")
    doc.append("")
    doc.append("**Parameters**")
    doc.append("- `settings` (dict): Options including `version` (1 or 2) and `compression_level` (0-9).")
    doc.append("")
    doc.append("**Returns**")
    doc.append("- `dict`: Configuration dictionary with keys `version` and `compression_level`.")
    doc.append("")
    doc.append("## encode(data, config)")
    doc.append("Encode data into a custom binary format with version header and optional compression.")
    doc.append("")
    doc.append("**Parameters**")
    doc.append("- `data` (bytes or str): Data to encode.")
    doc.append("- `config` (dict): Result of `configure_encoding()`.")
    doc.append("")
    doc.append("**Returns**")
    doc.append("- `bytes`: Encoded data prefixed with a 1-byte version header.")
    doc.append("")
    doc.append("## decode(encoded_data)")
    doc.append("Decode data produced by `encode()` back into raw bytes.")
    doc.append("")
    doc.append("**Parameters**")
    doc.append("- `encoded_data` (bytes): Data returned by `encode()`.")
    doc.append("")
    doc.append("**Returns**")
    doc.append("- `bytes`: Original uncompressed data.")
    doc.append("")
    doc.append("## document_api()")
    doc.append("Generate this API documentation string.")
    doc.append("")
    doc.append("**Returns**")
    doc.append("- `str`: Markdown-formatted documentation.")
    return "\n".join(doc)
