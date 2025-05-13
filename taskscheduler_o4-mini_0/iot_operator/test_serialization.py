import pytest
from iot_scheduler.serialization import serialize_job, deserialize_job

def test_pickle_serialization():
    obj = {'a': 1, 'b': [2,3]}
    data = serialize_job(obj)
    new = deserialize_job(data)
    assert new == obj

def test_msgpack_serialization_when_available():
    try:
        import msgpack  # noqa
    except ImportError:
        pytest.skip("msgpack not installed")
    obj = {'x': 9}
    data = serialize_job(obj, method='msgpack')
    new = deserialize_job(data, method='msgpack')
    assert new == obj
