import json

def validate_schema(msg, required_fields=None):
    if required_fields is None:
        required_fields = ['price', 'volume', 'symbol']
    if isinstance(msg, str):
        msg = json.loads(msg)
    if not isinstance(msg, dict):
        raise ValueError("Message must be a dict or JSON string")
    for field in required_fields:
        if field not in msg:
            raise ValueError(f"Missing field {field}")
    return msg
