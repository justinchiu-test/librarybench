import os
import sys

# Ensure the parent directory (which contains config_manager.py) is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
