"""
Validation logic for Translator CLI adapter.
"""
import os

def validate_input(i18n, locale, required_keys, placeholders, pattern, bundle_path):
    errors = []
    # Required keys
    for key in required_keys:
        if key not in i18n._data.get(locale, {}):
            errors.append(f"Missing translation for key: {key}")
    # Placeholders
    for name, template in placeholders.items():
        if f"{{{name}}}" not in template:
            errors.append(f"Invalid placeholder: {name}")
    # Pattern
    import re
    if not re.match(pattern, locale):
        errors.append(f"Locale {locale} does not match pattern")
    # Bundle path
    if not os.path.exists(bundle_path):
        errors.append("Bundle path does not exist")
    return errors