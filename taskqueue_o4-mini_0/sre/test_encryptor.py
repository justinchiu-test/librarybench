from task_queue.encryptor import Encryptor

def test_encrypt_decrypt():
    e = Encryptor(key=b'k')
    data = b'hello world'
    token = e.encrypt(data)
    assert token != data
    orig = e.decrypt(token)
    assert orig == data
