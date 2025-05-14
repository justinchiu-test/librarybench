import uuid
import secrets

def compute_default(token_type="uuid", length=16):
    if token_type == "uuid":
        return str(uuid.uuid4())
    elif token_type == "salt":
        return secrets.token_hex(length)
    else:
        raise ValueError("Unsupported token_type")
