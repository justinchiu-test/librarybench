"""
Secure secrets management for backend developers.
"""
def manage_secrets(service, key):
    if not service or not key:
        raise ValueError("Invalid service or key")
    # Dummy implementation
    return f"{service}:{key}"