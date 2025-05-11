import os
import json
import tempfile
import time  # added import

from api_startup.db_engine import DBEngine

def test_atomic_file_rename(tmp_path):
    path = tmp_path / "events.json"
    engine = DBEngine(path=str(path), encryption_key=b'k'*16)
    t = time.time()
    id1 = engine.upsert({'timestamp': t, 'userID': 'z', 'eventType': '1'})
    # check temp files cleaned
    dirfiles = os.listdir(str(tmp_path))
    assert all(not fname.endswith('.tmp') for fname in dirfiles)
