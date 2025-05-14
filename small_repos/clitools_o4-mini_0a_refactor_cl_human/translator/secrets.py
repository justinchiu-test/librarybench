import os

def get_secret(key, default=None):
    """
    Retrieve secret from environment variables.
    """
    return os.environ.get(key, default)
