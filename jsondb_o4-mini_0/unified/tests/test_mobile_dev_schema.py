import pytest
import time
from mobile_dev.journaling.schema import validate_entry, SchemaError

def make_valid():
    now = time.time()
    return {
        'id': '1',
        'content': 'Hello',
        'tags': ['a'],
        'attachments': [],
        'metadata': {},
        'created_at': now,
        'updated_at': now
    }

def test_valid_entry():
    entry = make_valid()
    validate_entry(entry)  # should not raise

@pytest.mark.parametrize('field', ['id','content','tags','attachments','metadata','created_at','updated_at'])
def test_missing_field(field):
    entry = make_valid()
    entry.pop(field)
    with pytest.raises(SchemaError):
        validate_entry(entry)

def test_bad_types():
    entry = make_valid()
    entry['id'] = 123
    with pytest.raises(SchemaError):
        validate_entry(entry)
    entry = make_valid()
    entry['tags'] = 'notalist'
    with pytest.raises(SchemaError):
        validate_entry(entry)

def test_created_after_updated():
    entry = make_valid()
    entry['created_at'] = entry['updated_at'] + 10
    with pytest.raises(SchemaError):
        validate_entry(entry)
