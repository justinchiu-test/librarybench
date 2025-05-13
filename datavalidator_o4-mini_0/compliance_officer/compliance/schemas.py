import yaml

# Central schema definition
SCHEMA = {
    "type": "object",
    "required": ["user_id", "data_retention_policy", "user_consent_status", "age"],
    "properties": {
        "user_id": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "data_retention_policy": {"enum": ["short_term", "long_term"]},
        "retention_period": {"type": "integer"},
        "user_consent_status": {"enum": ["granted", "revoked", "pending"]},
        "deletion_timestamp": {"type": "string"},
        "policy_version": {"type": "string"},
        "opt_out_reason": {"type": "string"},
        "pii_fields": {"type": "array", "items": {"type": "string"}}
    }
}

def export_schema(path):
    """
    Export the SCHEMA to a file at 'path' in YAML (JSON subset) format.
    """
    with open(path, "w") as f:
        yaml.dump(SCHEMA, f)

def import_schema(path):
    """
    Import schema from a YAML (JSON subset) file at 'path' and update SCHEMA in place.
    """
    with open(path) as f:
        data = yaml.safe_load(f)
    SCHEMA.clear()
    SCHEMA.update(data)
