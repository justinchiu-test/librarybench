"""
Secrets retrieval for security analysts.
"""
import os

def fetch_secret(uri):
    # Support gpg:// URIs for file-based secrets
    if uri.startswith('gpg://'):
        path = uri[len('gpg://'):]
        if not os.path.exists(path):
            raise FileNotFoundError(f"Secret file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    # Unsupported secret mechanisms
    if uri.startswith('kms://') or uri.startswith('vault://'):
        raise NotImplementedError(f"Secret backend not implemented: {uri.split('://')[0]}")
    raise ValueError(f"Unsupported URI scheme: {uri}")