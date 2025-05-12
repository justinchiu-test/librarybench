"""
Input validation for translator commands and configurations.
"""
import os
import re

def validate_input(i18n_obj, locale, required_keys=None, placeholders=None, pattern=None, bundle_path=None):
    errors = []
    # Required translations
    if required_keys:
        for key in required_keys:
            # translate returns key itself if missing
            if i18n_obj.translate(key, locale) == key:
                errors.append(f"Missing translation for key: {key}")
    # Placeholder validation
    if placeholders:
        for name, template in placeholders.items():
            placeholder_token = '{' + name + '}'
            if placeholder_token not in template:
                errors.append(f"Invalid placeholder: {name}")
    # Locale pattern
    if pattern:
        if not re.match(pattern, locale):
            errors.append(f"Locale {locale} does not match pattern")
    # Bundle existence
    if bundle_path:
        if not os.path.exists(bundle_path):
            errors.append("Bundle path does not exist")
    return errors