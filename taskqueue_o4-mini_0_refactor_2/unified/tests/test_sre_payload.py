from sre.task_queue.payload import Payload

def test_payload():
    desc = {'job':'backup'}
    data = b'\x00\x01'
    p = Payload(desc, data)
    assert p.descriptor == desc
    assert p.binary == data
