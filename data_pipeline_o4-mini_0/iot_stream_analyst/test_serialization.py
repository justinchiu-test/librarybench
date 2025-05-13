from streamkit.serialization import JSONSerialization

def test_serialize_dict():
    js = JSONSerialization()
    obj = {'a': 1, 'b': 'text'}
    s = js.serialize(obj)
    assert '"a": 1' in s and '"b": "text"' in s
