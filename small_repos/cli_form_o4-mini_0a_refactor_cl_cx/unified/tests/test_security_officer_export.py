from security_officer.incident_form.exporter import export_data
import json
import base64

def test_export_json_plain():
    data = {"a":1, "b":"two"}
    out = export_data(data, fmt="json", encrypt=False)
    loaded = json.loads(out)
    assert loaded == data

def test_export_yaml_plain():
    data = {"x": 10, "y": "yes"}
    out = export_data(data, fmt="yaml", encrypt=False)
    assert "x: 10" in out
    assert "y: yes" in out

def test_export_json_encrypted():
    data = {"k": "v"}
    token = export_data(data, fmt="json", encrypt=True)
    decoded = base64.b64decode(token.encode()).decode()
    assert '"k": "v"' in decoded

def test_export_yaml_encrypted():
    data = {"m": 5}
    token = export_data(data, fmt="yaml", encrypt=True)
    decoded = base64.b64decode(token.encode()).decode()
    assert "m: 5" in decoded
