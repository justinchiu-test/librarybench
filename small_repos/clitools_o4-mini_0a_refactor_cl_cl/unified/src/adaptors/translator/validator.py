"""Adapter for translator.validator."""

from typing import Dict, Any, List, Union, Optional
from ...utils.validation import validate_type, validate_pattern, validate_range

def validate_string(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None, pattern: Optional[str] = None) -> bool:
    """Validate a string value.
    
    Args:
        value (str): String to validate
        min_length (int, optional): Minimum length
        max_length (int, optional): Maximum length
        pattern (str, optional): Regex pattern
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not validate_type(value, str):
        return False
        
    length_valid = True
    if min_length is not None and len(value) < min_length:
        length_valid = False
    if max_length is not None and len(value) > max_length:
        length_valid = False
        
    if not length_valid:
        return False
        
    if pattern is not None and not validate_pattern(value, pattern):
        return False
        
    return True
