"""
Default value generators for security analysts.
"""
import uuid
import os
import binascii

def compute_default(kind, length=None):
    if kind == 'uuid':
        return str(uuid.uuid4())
    if kind == 'salt':
        # length in bytes; default 16 bytes
        length = length or 16
        return binascii.hexlify(os.urandom(length)).decode('utf-8')
    raise ValueError(f"Unknown default kind: {kind}")