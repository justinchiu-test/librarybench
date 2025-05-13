# secret_decryption
import base64

def decrypt_value(val: str) -> str:
    """
    Decrypt a value if it's encrypted.
    Recognizes:
      - BASE64:<base64_data>
      - ENC[AES]:<base64_data>
    """
    if val.startswith("BASE64:"):
        b = val.split("BASE64:", 1)[1]
        return base64.b64decode(b).decode('utf-8')
    if val.startswith("ENC[AES]:"):
        b = val.split("ENC[AES]:", 1)[1]
        # Stub AES decryption: just base64-decode
        return base64.b64decode(b).decode('utf-8')
    return val
