import os
import sys

# Ensure src/ is on PYTHONPATH so our unified packages can be imported
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)