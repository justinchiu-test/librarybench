from flask import request, jsonify

def parse_json():
    """
    Safely parse JSON from Flask request.
    Returns an empty dict if no JSON is provided.
    """
    return request.get_json(silent=True) or {}

def require_fields(data: dict, *fields):
    """
    Ensure that `data` contains all of the specified `fields`.
    Raises ValueError if any are missing or None.
    Returns a list of the field values, in order.
    """
    missing = [f for f in fields if data.get(f) is None]
    if missing:
        raise ValueError(f"Missing {', '.join(missing)!r}")
    return [data[f] for f in fields]

def ok(data=None, code=200):
    """
    Return a standard Flask JSON success response.
    """
    return jsonify(data or {}), code

def error(message: str, code=400):
    """
    Return a standard Flask JSON error response.
    """
    return jsonify({"error": message}), code
