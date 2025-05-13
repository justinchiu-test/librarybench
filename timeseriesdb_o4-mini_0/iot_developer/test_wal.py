import os
from pathlib import Path
import tempfile
from iotdb.wal import WriteAheadLog

def test_wal_append_replay(tmp_path):
    path = tmp_path / 'wal.log'
    wal = WriteAheadLog(str(path))
    wal.append({'x':1})
    wal.append({'y':2})
    recs = wal.replay()
    assert recs == [{'x':1}, {'y':2}]
