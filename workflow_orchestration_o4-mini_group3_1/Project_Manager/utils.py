# Shared utility functions for all modules
# IMPORTANT: This file must work when imported by different modules in different directories

from flask import jsonify

def json_response(payload: dict, status: int = 200):
    """
    Return a Flask JSON response tuple (body, status).
    """
    return jsonify(payload), status

def error_response(message: str, status: int):
    """
    Return a standardized error JSON response.
    """
    return json_response({"error": message}, status)
