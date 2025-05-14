import os
import json

def validate_schema(schema, data, schema_name="schema", storage_dir="."):
    valid = True
    # Basic manual validation for simple object schemas
    try:
        # Check object type
        if schema.get("type") == "object":
            if not isinstance(data, dict):
                valid = False
            else:
                # Required properties
                for req in schema.get("required", []):
                    if req not in data:
                        valid = False
                        break
                # Property type checks
                if valid:
                    for key, subschema in schema.get("properties", {}).items():
                        if key in data:
                            expected = subschema.get("type")
                            if expected == "number":
                                if not isinstance(data[key], (int, float)):
                                    valid = False
                                    break
                            elif expected == "string":
                                if not isinstance(data[key], str):
                                    valid = False
                                    break
                            elif expected == "object":
                                if not isinstance(data[key], dict):
                                    valid = False
                                    break
                            elif expected == "array":
                                if not isinstance(data[key], list):
                                    valid = False
                                    break
        # Could add other schema types here if needed
    except Exception:
        valid = False

    if valid:
        return True

    # On validation failure, write the invalid record
    os.makedirs(storage_dir, exist_ok=True)
    path = os.path.join(storage_dir, f"{schema_name}_invalid_records.jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")
    return False
