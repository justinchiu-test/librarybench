import pytest
from scheduler.serialization import serialize_job, deserialize_job

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

def test_json_serialization():
    obj = {'a': 1}
    data = serialize_job(obj, format='json')
    assert isinstance(data, bytes)
    out = deserialize_job(data, format='json')
    assert out == obj

def test_pickle_serialization():
    obj = {'b': 2}
    data = serialize_job(obj, format='pickle')
    out = deserialize_job(data, format='pickle')
    assert out == obj

@pytest.mark.skipif(not MSGPACK_AVAILABLE, reason="msgpack not available")
def test_msgpack_serialization():
    obj = {'c': 3}
    data = serialize_job(obj, format='msgpack')
    out = deserialize_job(data, format='msgpack')
    assert out == obj

def test_unknown_format():
    with pytest.raises(ValueError):
        serialize_job({'a':1}, format='xml')
    with pytest.raises(ValueError):
        deserialize_job(b'', format='xml')
