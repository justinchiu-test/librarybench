import base64

def decrypt_secret(blob):
    if blob.startswith("AES:"):
        ciphertext = blob[4:]
        return ciphertext[::-1]
    try:
        decoded = base64.b64decode(blob)
        return decoded.decode("utf-8")
    except Exception:
        return blob
