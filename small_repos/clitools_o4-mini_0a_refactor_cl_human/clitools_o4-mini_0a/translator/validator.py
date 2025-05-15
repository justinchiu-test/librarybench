import os
import re
from i18n import I18n

def validate_input(i18n, locale, required_keys, placeholders=None, pattern=None, bundle_path=None):
    """
    Validate translation inputs:
    - required_keys present in translations
    - placeholders must exist in texts
    - locale matches regex pattern
    - bundle_path exists on filesystem
    Returns list of error messages (empty if all valid).
    """
    errors = []
    # Missing translation keys
    for key in required_keys:
        if i18n.translate(key, locale) == key:
            errors.append(f"Missing translation for key: {key}")
    # Placeholder checks
    if placeholders:
        for name, text in placeholders.items():
            if f"{{{name}}}" not in text:
                errors.append(f"Invalid placeholder: {name} in text: {text}")
    # Pattern check
    if pattern:
        if not re.fullmatch(pattern, locale):
            errors.append(f"Locale {locale} does not match pattern {pattern}")
    # Bundle path check
    if bundle_path:
        if not os.path.exists(bundle_path):
            errors.append(f"Bundle path does not exist: {bundle_path}")
    return errors
