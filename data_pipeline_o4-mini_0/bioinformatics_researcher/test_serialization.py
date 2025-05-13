import json
from pipeline.serialization import JSONSerializer, YAMLSerializer

def test_json_serializer():
    data = {'a': 1}
    s = JSONSerializer.serialize(data)
    assert json.loads(s) == data

def test_yaml_serializer():
    data = {'a': 1}
    s = YAMLSerializer.serialize(data)
    assert 'a:' in s
