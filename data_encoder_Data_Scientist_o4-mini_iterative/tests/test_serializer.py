import pytest
import json
import yaml
import xml.etree.ElementTree as ET
import hashlib

from src.serializer import DataTransformer, SerializerError

@pytest.fixture
def transformer():
    return DataTransformer()

simple_data = {
    'name': 'Alice',
    'age': 30,
    'score': 95.5,
    'active': True,
    'preferences': None
}

nested_data = {
    'user': simple_data,
    'tags': ['python', 'testing'],
    'stats': {
        'min': 0,
        'max': 100,
        'values': [1, 2, 3]
    }
}

def test_json_round_trip(transformer):
    s = transformer.serialize(simple_data, 'json')
    assert isinstance(s, str)
    d = transformer.deserialize(s, 'json')
    assert d == simple_data

def test_yaml_round_trip(transformer):
    s = transformer.serialize(simple_data, 'yaml')
    assert isinstance(s, str)
    d = transformer.deserialize(s, 'yaml')
    assert d == simple_data

def test_xml_round_trip_simple(transformer):
    s = transformer.serialize(simple_data, 'xml')
    assert s.startswith('<root>')
    d = transformer.deserialize(s, 'xml')
    assert d == simple_data

def test_xml_round_trip_nested(transformer):
    s = transformer.serialize(nested_data, 'xml')
    d = transformer.deserialize(s, 'xml')
    assert d == nested_data

def test_cross_language_support(transformer):
    for fmt in transformer.SUPPORTED_FORMATS:
        serialized, deserialized, ok = transformer.cross_language_support(nested_data, fmt)
        assert ok
        if fmt == 'json':
            assert json.loads(serialized) == nested_data
        elif fmt == 'yaml':
            assert yaml.safe_load(serialized) == nested_data
        elif fmt == 'xml':
            # should parse without error
            ET.fromstring(serialized)

def test_data_integrity_checks(transformer):
    checks = transformer.data_integrity_checks(simple_data)
    assert set(checks.keys()) == set(transformer.SUPPORTED_FORMATS)
    for fmt, result in checks.items():
        assert result['round_trip'] is True
        checksum = result['checksum']
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex length
        # Recompute and compare
        serialized = transformer.serialize(simple_data, fmt)
        expected = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        assert checksum == expected

def test_nested_structures(transformer):
    results = transformer.nested_structures(nested_data)
    for fmt, result in results.items():
        assert result['round_trip'] is True

def test_unsupported_format(transformer):
    with pytest.raises(SerializerError):
        transformer.serialize(simple_data, 'binary')
    with pytest.raises(SerializerError):
        transformer.deserialize("{}", 'binary')

def test_unit_testing_hint(transformer):
    hint = transformer.unit_testing()
    assert 'pytest' in hint
