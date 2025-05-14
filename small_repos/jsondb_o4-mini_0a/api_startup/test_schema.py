import pytest
from db_engine import DBEngine

def test_missing_fields():
    engine = DBEngine(path=':memory:', encryption_key=b'k')
    with pytest.raises(ValueError):
        engine.enforce_schema({'timestamp': 1})
    with pytest.raises(ValueError):
        engine.enforce_schema({'userID': 'u', 'eventType': 'e'})
    # passes
    engine.enforce_schema({'timestamp': 1.0, 'userID': 'u', 'eventType': 'e'})
