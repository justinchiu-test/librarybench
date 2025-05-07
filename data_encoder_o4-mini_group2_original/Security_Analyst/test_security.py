import logging
import base64
import pytest
from Security_Analyst.security import encrypt_data, log_operation, logger

def test_encrypt_decrypt_cycle():
    key = "secretkey"
    data = "Hello, World!"
    encrypted = encrypt_data(data, key)
    assert isinstance(encrypted, str)
    # Ensure ciphertext does not contain plaintext
    assert data not in encrypted

    # Manually decrypt: base64-decode then XOR with key
    encrypted_bytes = base64.b64decode(encrypted.encode("utf-8"))
    key_bytes = key.encode("utf-8")
    decrypted = bytes(
        encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)]
        for i in range(len(encrypted_bytes))
    ).decode("utf-8")
    assert decrypted == data

def test_same_input_same_output():
    data = "consistent"
    key = "key123"
    enc1 = encrypt_data(data, key)
    enc2 = encrypt_data(data, key)
    assert enc1 == enc2

def test_empty_string_encryption():
    data = ""
    key = "anykey"
    enc = encrypt_data(data, key)
    # Base64 of empty bytes is empty string
    assert enc == ""

def test_non_str_inputs_raise_type_error():
    with pytest.raises(TypeError):
        encrypt_data(123, "key")
    with pytest.raises(TypeError):
        encrypt_data("data", 456)

def test_non_ascii_characters():
    data = "こんにちは世界"  # "Hello World" in Japanese
    key = "秘密"            # "secret" in Japanese
    encrypted = encrypt_data(data, key)
    assert isinstance(encrypted, str)

    # Decrypt back
    encrypted_bytes = base64.b64decode(encrypted.encode("utf-8"))
    key_bytes = key.encode("utf-8")
    decrypted = bytes(
        encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)]
        for i in range(len(encrypted_bytes))
    ).decode("utf-8")
    assert decrypted == data

def test_log_operation_logs_info(caplog):
    caplog.set_level(logging.INFO)
    operation = "ENCODE"
    details = {"length": 12, "status": "ok"}
    log_operation(operation, details)
    # Ensure a log record with the correct message exists
    expected_message = f"{operation} - {details}"
    assert any(expected_message == rec.getMessage() for rec in caplog.records)

def test_log_operation_invalid_args():
    with pytest.raises(TypeError):
        log_operation(123, {"a": 1})
    with pytest.raises(TypeError):
        log_operation("OP", "not_a_dict")
