import os

def generate_key(length=16):
    """Generate a random symmetric key of given length."""
    return os.urandom(length)

def encrypt_file(input_path, output_path, key):
    """Encrypt file content via XOR cipher and write to output."""
    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    with open(output_path, 'wb') as f_out:
        f_out.write(encrypted)

def decrypt_file(input_path, output_path, key):
    """Decrypt file content via XOR cipher and write to output."""
    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    # symmetric XOR
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    with open(output_path, 'wb') as f_out:
        f_out.write(decrypted)
