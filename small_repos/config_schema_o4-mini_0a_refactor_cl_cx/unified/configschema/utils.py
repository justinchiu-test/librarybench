"""
Utility functions for prompting missing values.
"""
from .error import ValidationError

def prompt_missing(name, expected_type):
    """
    Prompt the user to input a missing configuration value.
    Returns the value cast to expected_type, or raises ValidationError on failure.
    """
    # Keep prompting until valid input is provided
    while True:
        raw = input(f"{name}: ")
        # For list type, split on comma
        if expected_type == list:
            return raw.split(',') if raw else []
        try:
            return expected_type(raw)
        except Exception:
            # invalid input, prompt again
            continue