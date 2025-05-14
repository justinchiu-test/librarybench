def format_error(field, message, highlight=True):
    """
    Format error message; if highlight, wrap with markers.
    """
    if highlight:
        return f"**ERROR** {field}: {message}"
    else:
        return f"ERROR {field}: {message}"
