"""
Security module providing data encryption and operation logging.
"""
import logging
from base64 import b64encode

logger = logging.getLogger(__name__)

def encrypt_data(data, encryption_key):
    """
    Encrypts the input data using a simple XOR cipher with the provided encryption_key.
    Returns a base64-encoded string of the encrypted data.
    """
    if not isinstance(data, str):
        raise TypeError("data must be a string")
    if not isinstance(encryption_key, str):
        raise TypeError("encryption_key must be a string")
    data_bytes = data.encode("utf-8")
    key_bytes = encryption_key.encode("utf-8")
    # If there's no data, return empty string
    if not data_bytes:
        return ""
    # XOR each byte with the key (cycled) and base64-encode the result
    encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes))
    return b64encode(encrypted).decode("utf-8")

def log_operation(operation_type, details):
    """
    Logs the operation_type and details using the configured logger.
    """
    if not isinstance(operation_type, str):
        raise TypeError("operation_type must be a string")
    if not isinstance(details, dict):
        raise TypeError("details must be a dictionary")
    message = f"{operation_type} - {details}"
    logger.info(message)
