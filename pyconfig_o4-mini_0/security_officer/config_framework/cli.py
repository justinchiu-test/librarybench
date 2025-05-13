def confirm_setting(key, value):
    resp = input(f"Apply setting {key}={value}? (y/n): ").strip().lower()
    return resp == "y"
