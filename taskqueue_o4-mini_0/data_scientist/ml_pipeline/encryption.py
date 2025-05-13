from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(input_path, output_path, key):
    cipher = Fernet(key)
    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    token = cipher.encrypt(data)
    with open(output_path, 'wb') as f_out:
        f_out.write(token)

def decrypt_file(input_path, output_path, key):
    cipher = Fernet(key)
    with open(input_path, 'rb') as f_in:
        token = f_in.read()
    data = cipher.decrypt(token)
    with open(output_path, 'wb') as f_out:
        f_out.write(data)
