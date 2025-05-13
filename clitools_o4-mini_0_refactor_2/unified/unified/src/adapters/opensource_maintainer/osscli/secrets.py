"""
Secret fetching for Open Source Maintainer CLI.
Supports env and file backends.
"""
import os

def fetch_secret(backend, key=None, path=None):
    if backend == 'env':
        return os.getenv(key)
    if backend == 'file':
        if not path:
            raise ValueError('Missing path for file backend')
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        val = open(path, 'r').read().rstrip('\n')
        return val
    raise ValueError(f"Unknown backend: {backend}")