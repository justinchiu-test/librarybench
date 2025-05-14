import yaml
import os
import tempfile
from compliance.schemas import SCHEMA, export_schema, import_schema

def test_export_import_schema(tmp_path):
    temp_file = tmp_path / "schema.yaml"
    original = dict(SCHEMA)
    export_schema(str(temp_file))
    # mutate file
    data = yaml.safe_load(open(temp_file))
    data["properties"]["new_field"] = {"type": "string"}
    with open(temp_file, "w") as f:
        yaml.dump(data, f)
    import_schema(str(temp_file))
    assert "new_field" in SCHEMA["properties"]
    # restore original
    SCHEMA.clear()
    SCHEMA.update(original)
