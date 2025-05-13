"""
Version bump utility for Security Analyst CLI.
"""
import re

def bump_version(tags):
    # tags: list of version strings
    latest = None
    for tag in tags:
        parts = tag.split('.')
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            nums = tuple(map(int, parts))
            if latest is None or nums > latest:
                latest = nums
    if latest is None:
        return '0.0.1'
    major, minor, patch = latest
    patch += 1
    return f"{major}.{minor}.{patch}"