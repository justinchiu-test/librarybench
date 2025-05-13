class ConfigError(Exception):
    pass

def report_error(filename, lineno, section, key, expected, actual, suggestion=None):
    msg = (f"{filename}:{lineno}: Error in section '{section}', key '{key}': "
           f"expected {expected}, got {actual}.")
    if suggestion:
        msg += f" Suggestion: {suggestion}"
    return msg
