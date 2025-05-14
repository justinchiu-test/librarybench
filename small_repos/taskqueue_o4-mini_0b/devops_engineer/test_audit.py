import os
from taskqueue.queue import TaskQueue, _xor_decrypt

def test_audit_logging(tmp_path):
    data_dir = tmp_path
    q = TaskQueue(data_dir=str(data_dir))
    tid = q.enqueue('p')
    path = os.path.join(str(data_dir), 'audit.log')
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        data = f.read()
    dec = _xor_decrypt(data, q.key)
    lines = dec.decode().splitlines()
    assert any('enqueue' in line and tid in line for line in lines)
