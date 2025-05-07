import json
import pytest
from system_architect.streaming_support import streaming_support

def test_encode_objects_to_bytes():
    data = [{'a': 1}, {'b': 'test'}]
    result = list(streaming_support(data))
    assert all(isinstance(item, bytes) for item in result)
    decoded = [json.loads(item.decode('utf-8')) for item in result]
    assert decoded == data

def test_decode_bytes_to_objects():
    data = [{'x': 10}, {'y': 'hello'}]
    bytes_data = [json.dumps(obj).encode('utf-8') + b'\n' for obj in data]
    result = list(streaming_support(bytes_data))
    assert result == data

def test_decode_strings_to_objects():
    data = [{'m': True}, {'n': None}]
    str_data = [json.dumps(obj) + '\n' for obj in data]
    result = list(streaming_support(str_data))
    assert result == data

def test_empty_and_blank_items_are_skipped():
    # Empty bytes or strings should be skipped
    items = [b'', '', {'a':1}]
    result = list(streaming_support(items))
    assert result == [{'a':1}]
