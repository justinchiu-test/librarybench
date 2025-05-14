import pytest
from etl.pipeline import ETLPipeline

class JSONSerializer:
    def serialize(self, data):
        import json
        return json.dumps(data)
    def deserialize(self, data):
        import json
        return json.loads(data)

def test_json_serializer_integration():
    p = ETLPipeline()
    serializer = JSONSerializer()
    p.registerSerializer('json', serializer)
    assert 'json' in p.serializer_registry
    # round-trip serialize/deserialize
    obj = {'a': 1, 'b': [1,2,3]}
    raw = serializer.serialize(obj)
    back = serializer.deserialize(raw)
    assert back == obj

def test_publish_with_no_serializer():
    p = ETLPipeline()
    def identity(x):
        return x
    events = ['a', 'b']
    p.publishSync(events, identity)
    assert p.event_store['raw'] == events
    assert p.event_store['processed'] == events
