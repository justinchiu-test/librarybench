import pytest
from etllib.serializers import JSONSerialization, YAMLSerialization

def test_json_serialization_roundtrip():
    data = {'a': 1, 'b': [2, 3]}
    s = JSONSerialization.dumps(data)
    assert isinstance(s, str)
    obj = JSONSerialization.loads(s)
    assert obj == data

def test_yaml_serialization_roundtrip():
    data = {'x': 10, 'y': ['hello', 'world']}
    s = YAMLSerialization.dumps(data)
    assert isinstance(s, str)
    obj = YAMLSerialization.loads(s)
    assert obj == data
