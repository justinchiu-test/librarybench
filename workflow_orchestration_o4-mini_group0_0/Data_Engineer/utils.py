from fastapi import HTTPException
from flask import jsonify

def get_or_404(result, message="Not found"):
    """
    FastAPI: return result or raise 404 HTTPException.
    """
    if result is None:
        raise HTTPException(status_code=404, detail=message)
    return result

def assert_true_or_404(ok, message="Not found"):
    """
    FastAPI: assert a boolean, else raise 404 HTTPException.
    """
    if not ok:
        raise HTTPException(status_code=404, detail=message)
    return True

def require_fields(data: dict, *fields):
    """
    Flask: ensure that all 'fields' exist in data dict.
    Returns (True, None) or (False, error_message).
    """
    missing = [f for f in fields if f not in data]
    if missing:
        names = ", ".join(repr(f) for f in missing)
        return False, f"Missing {names}"
    return True, None

def flask_json_response(data, status=200):
    """
    Flask: JSONify data with given status code.
    """
    return jsonify(data), status

def flask_error(message, status=400):
    """
    Flask: return JSON error with given status code.
    """
    return jsonify({"error": message}), status
