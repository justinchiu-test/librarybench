"""
Secret fetching for Security Analyst CLI.
Supports gpg scheme, others not implemented.
"""
import os
from urllib.parse import urlparse

def fetch_secret(uri):
    parsed = urlparse(uri)
    scheme = parsed.scheme
    if scheme == 'gpg':
        path = parsed.path
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        return open(path, 'r').read().rstrip('\n')
    if scheme in ('kms', 'vault'):
        raise NotImplementedError(f"Scheme not supported: {scheme}")
    raise ValueError(f"Invalid URI: {uri}")