import os
import tempfile
from api_startup.db_engine import DBEngine

def test_encryption_writes_obfuscated():
    dirpath = tempfile.mkdtemp()
    path = os.path.join(dirpath, 'events.json')
    key = b'abcdefghijklmnop'
    engine = DBEngine(path=path, encryption_key=key)
    eid = engine.upsert({'timestamp': 0, 'userID': 'u', 'eventType': 'e'})
    with open(path, 'rb') as f:
        data = f.read()
    # decrypt manually
    plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    assert b'"userID": "u"' in plain
    # ensure encrypted file does not contain plaintext
    assert b'"userID": "u"' not in data
