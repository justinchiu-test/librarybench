import base64
try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None

def decrypt_base64(data):
    return base64.b64decode(data)

def decrypt_aes(data, key):
    if AES is None:
        raise NotImplementedError("AES decryption requires pycryptodome")
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(data)
