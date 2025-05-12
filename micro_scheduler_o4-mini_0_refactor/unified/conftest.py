import sys
import os

# Ensure src directory is on PYTHONPATH for imports
root_dir = os.path.dirname(__file__)
src_path = os.path.join(root_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)