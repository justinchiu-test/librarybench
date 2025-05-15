import os
import re

def validate_input(i18n, locale, required_keys=None, placeholders=None, pattern=None, bundle_path=None):
    """
    Validate translation input
    
    Args:
        i18n: I18n instance
        locale: Locale to validate
        required_keys: List of required translation keys
        placeholders: Dictionary of placeholder text with required placeholders
        pattern: Regular expression pattern for valid locales
        bundle_path: Path to translation bundle file
        
    Returns:
        list: List of validation errors (empty if all valid)
    """
    errors = []
    
    # Check locale against pattern
    if pattern and not re.match(pattern, locale):
        errors.append(f"Locale {locale} does not match pattern {pattern}")
    
    # Check required keys
    if required_keys:
        for key in required_keys:
            if locale in i18n.translations:
                if key not in i18n.translations[locale]:
                    errors.append(f"Missing translation for key: {key}")
    
    # Check placeholders
    if placeholders:
        for key, text in placeholders.items():
            # Check if the placeholder is actually in the text
            placeholder_pattern = r'\{' + key + r'\}'
            if not re.search(placeholder_pattern, text):
                errors.append(f"Invalid placeholder: {key} in text: {text}")
    
    # Check bundle path exists
    if bundle_path and not os.path.exists(bundle_path):
        errors.append(f"Bundle path does not exist: {bundle_path}")
    
    return errors