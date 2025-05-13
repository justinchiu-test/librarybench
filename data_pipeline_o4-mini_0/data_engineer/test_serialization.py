import pytest
from pipeline.serialization import JSONSerialization, YAMLSerialization

def test_json_serialization():
    data = {'a': 1, 'b': 'test'}
    s = JSONSerialization.dumps(data)
    assert JSONSerialization.loads(s) == data

def test_yaml_serialization():
    data = {'x': [1,2,3], 'y': {'nested': True}}
    s = YAMLSerialization.dumps(data)
    assert YAMLSerialization.loads(s) == data
