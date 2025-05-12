"""
Secrets management for data scientists.
"""
import os

def manage_secrets(keys):
    store = os.environ.get('SECRET_STORE')
    if store != 'env':
        raise ValueError('Unsupported secret store')
    result = {}
    for key in keys:
        if key in os.environ:
            result[key] = os.environ[key]
        else:
            raise KeyError(key)
    return result