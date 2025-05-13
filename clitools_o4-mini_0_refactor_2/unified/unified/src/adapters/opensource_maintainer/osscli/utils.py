"""
Utility functions for Open Source Maintainer CLI.
"""
import datetime
import uuid
import re

def compute_default(name):
    if name == 'build_dir':
        return 'build'
    if name == 'docs_dir':
        return 'docs_' + datetime.datetime.utcnow().strftime('%Y%m%d')
    if name == 'token':
        return uuid.uuid4().hex[:16]
    return None