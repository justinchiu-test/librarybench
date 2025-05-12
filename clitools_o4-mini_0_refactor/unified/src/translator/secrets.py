"""
Secret retrieval for translator.
"""
import os

def get_secret(key, default=None):
    return os.environ.get(key, default)