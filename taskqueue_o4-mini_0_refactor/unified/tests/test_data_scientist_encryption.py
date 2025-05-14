import os
import tempfile
from data_scientist.ml_pipeline.encryption import generate_key, encrypt_file, decrypt_file

def test_encrypt_decrypt(tmp_path):
    key = generate_key()
    data = b"secret data"
    infile = tmp_path / "in.txt"
    encfile = tmp_path / "enc.dat"
    decfile = tmp_path / "dec.txt"
    infile.write_bytes(data)
    encrypt_file(str(infile), str(encfile), key)
    assert encfile.exists()
    decrypt_file(str(encfile), str(decfile), key)
    assert decfile.read_bytes() == data
