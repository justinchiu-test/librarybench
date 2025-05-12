"""
Secret retrieval for open-source maintainers.
"""
import os

def fetch_secret(backend, key=None, path=None):
    if backend == 'env':
        return os.environ.get(key)
    if backend == 'file':
        if not path:
            raise ValueError('Path is required for file backend')
        if not os.path.exists(path):
            raise ValueError(f'File not found: {path}')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().rstrip('\n')
    raise ValueError(f'Unknown backend: {backend}')