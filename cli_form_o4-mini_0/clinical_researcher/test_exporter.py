import json
import pytest
from form_system.exporter import export_data

def test_export_json():
    data = {'a': 1, 'b': 'x'}
    out = export_data(data, format='json')
    assert isinstance(out, str)
    loaded = json.loads(out)
    assert loaded == data

def test_export_python():
    data = {'x': 2}
    out = export_data(data, format='python')
    assert out == data

def test_export_yaml():
    data = {'k': 'v', 'n': 3}
    out = export_data(data, format='yaml')
    # simple check for YAML key presence
    assert 'k:' in out
    assert 'n:' in out

def test_export_unsupported():
    with pytest.raises(ValueError):
        export_data({}, format='xml')
