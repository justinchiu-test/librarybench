import base64
import json

def encrypt(data_bytes, key):
    return base64.b64encode(data_bytes)

def decrypt(enc_bytes, key):
    return base64.b64decode(enc_bytes)
