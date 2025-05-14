from datetime import datetime
from jsonschema import ValidationError

# Allowed schema definitions
_REQUIRED_FIELDS = {"auditID", "userID", "eventSeverity", "timestamp", "message"}
_ALLOWED_FIELDS = _REQUIRED_FIELDS.union({"status"})
_SEVERITY_ENUM = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
_STATUS_ENUM = {"active", "archived"}

def enforce_schema(record: dict):
    # Must be a dict
    if not isinstance(record, dict):
        raise ValidationError("Record must be an object")

    # Check for required fields
    missing = _REQUIRED_FIELDS - record.keys()
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(sorted(missing))}")

    # No extra fields
    extra = set(record.keys()) - _ALLOWED_FIELDS
    if extra:
        raise ValidationError(f"Unexpected field(s): {', '.join(sorted(extra))}")

    # Type and enum checks
    # auditID
    if not isinstance(record["auditID"], str):
        raise ValidationError("auditID must be a string")
    # userID
    if not isinstance(record["userID"], str):
        raise ValidationError("userID must be a string")
    # eventSeverity
    sev = record["eventSeverity"]
    if not isinstance(sev, str) or sev not in _SEVERITY_ENUM:
        raise ValidationError(f"eventSeverity must be one of {sorted(_SEVERITY_ENUM)}")
    # timestamp
    ts = record["timestamp"]
    if not isinstance(ts, str):
        raise ValidationError("timestamp must be a string in ISO format")
    try:
        datetime.fromisoformat(ts)
    except Exception:
        raise ValidationError("timestamp is not a valid ISO datetime")
    # message
    if not isinstance(record["message"], str):
        raise ValidationError("message must be a string")
    # status (optional)
    if "status" in record:
        st = record["status"]
        if not isinstance(st, str) or st not in _STATUS_ENUM:
            raise ValidationError(f"status must be one of {sorted(_STATUS_ENUM)}")

    return True
