import json
from pathlib import Path
import tempfile
from iotdb.utils import json_import, tag_pattern_query

def test_json_import(tmp_path):
    path = tmp_path / 'data.json'
    data = [{'a':1}, {'b':2}]
    path.write_text(json.dumps(data))
    assert json_import(str(path)) == data

def test_tag_pattern_query():
    devices = {
        'd1': {'room':'living1', 'type':'temp'},
        'd2': {'room':'living2', 'type':'hum'}
    }
    res = tag_pattern_query(devices, 'room:living*')
    assert set(res) == {'d1', 'd2'}
    res = tag_pattern_query(devices, 'type:temp')
    assert res == ['d1']
