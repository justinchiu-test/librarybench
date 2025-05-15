def format_error(message, critical=False):
    if critical:
        return f"*** ERROR: {message} ***"
    else:
        return f"ERROR: {message}"
