"""
Input validation for translator CLI tools.
"""

import os
import re
from typing import Dict, Any, List, Optional
from translator.i18n import I18n


def validate_input(
    i18n: I18n,
    locale: str,
    required_keys: List[str],
    placeholders: Dict[str, str],
    pattern: str,
    bundle_path: str
) -> List[str]:
    """
    Validate translation input.
    
    Args:
        i18n (I18n): I18n instance.
        locale (str): Locale code.
        required_keys (List[str]): List of required translation keys.
        placeholders (Dict[str, str]): Dictionary mapping placeholder names to example text.
        pattern (str): Regex pattern for valid locale codes.
        bundle_path (str): Path to translation bundle file.
        
    Returns:
        List[str]: List of validation errors, empty if input is valid.
    """
    errors = []
    
    # Validate locale pattern
    if not re.match(pattern, locale):
        errors.append(f"Locale {locale} does not match pattern {pattern}")
    
    # Validate required keys
    for key in required_keys:
        translation = i18n.translate(key, locale)
        if translation == key:  # Key not found
            errors.append(f"Missing translation for key: {key}")
    
    # Validate placeholders
    for name, example in placeholders.items():
        if "{" + name + "}" not in example:
            errors.append(f"Invalid placeholder: {name}")
    
    # Validate bundle path
    if not os.path.exists(bundle_path):
        errors.append(f"Bundle path does not exist: {bundle_path}")
    
    return errors