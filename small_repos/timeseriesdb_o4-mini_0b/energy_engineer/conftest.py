import sys
import os
import importlib

# Starting point for our search: the directory where this conftest.py lives
HERE = os.path.dirname(__file__)

# Walk the tree looking for the directory that actually contains your platform.py
code_dir = None
for root, dirs, files in os.walk(HERE):
    if 'platform.py' in files:
        code_dir = root
        break

# If we found it, insert it at the front of sys.path so "import platform" picks up yours
if code_dir:
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
else:
    # Fallback: at least add the top directory in case tests & code are colocated
    if HERE not in sys.path:
        sys.path.insert(0, HERE)

# Now force‐override the stdlib platform module with our local one
try:
    local_platform = importlib.import_module('platform')
    sys.modules['platform'] = local_platform
except ImportError:
    # If it truly isn't there, let things error out in the tests themselves
    pass
