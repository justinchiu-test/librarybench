import os
import sys

# Insert the project root (one level up from tests/) into sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if root not in sys.path:
    sys.path.insert(0, root)
