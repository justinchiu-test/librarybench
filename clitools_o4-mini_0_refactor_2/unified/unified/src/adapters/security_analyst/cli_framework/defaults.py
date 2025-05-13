"""
Default value computation for Security Analyst CLI.
"""
import uuid
import datetime

def compute_default(kind, length=8):
    if kind == 'uuid':
        return str(uuid.uuid4())
    if kind == 'salt':
        # Generate hex string of length*2
        return uuid.uuid4().hex[:length*2]
    return None