import os
import sys

# Ensure that the directory containing codec.py is on sys.path,
# so that `import codec` in tests will find our module.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
