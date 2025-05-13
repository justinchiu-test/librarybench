from config_loader.decryption import decrypt_value
import base64

def test_decrypt_base64():
    s = base64.b64encode(b'test').decode('utf-8')
    assert decrypt_value(f"BASE64:{s}") == 'test'

def test_decrypt_aes_stub():
    s = base64.b64encode(b'secret').decode('utf-8')
    assert decrypt_value(f"ENC[AES]:{s}") == 'secret'

def test_decrypt_plain():
    assert decrypt_value('plain') == 'plain'
