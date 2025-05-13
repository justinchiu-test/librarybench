"""
Manage secrets for data_scientist datapipeline CLI.
Supports environment-backed secrets.
"""
import os

def manage_secrets(keys):
    store = os.getenv('SECRET_STORE', 'env')
    if store != 'env':
        raise NotImplementedError(f"Store {store} not supported")
    result = {}
    for k in keys:
        v = os.getenv(k)
        if v is None:
            raise KeyError(k)
        result[k] = v
    return result