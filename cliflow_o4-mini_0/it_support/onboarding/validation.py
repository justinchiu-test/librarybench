import re

def validate_username(username):
    if not re.fullmatch(r"\w+", username):
        raise ValueError("Invalid username")
    return True

def validate_department(dept):
    if not re.fullmatch(r"[A-Z]{2,4}", dept):
        raise ValueError("Invalid department code")
    return True

def validate_license_key(key):
    if not re.fullmatch(r"[A-Z0-9]{4}(?:-[A-Z0-9]{4}){3}", key):
        raise ValueError("Invalid license key")
    return True

def validate_params(username, dept, license_key):
    validate_username(username)
    validate_department(dept)
    validate_license_key(license_key)
    return True
