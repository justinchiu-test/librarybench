import sys
import os

# ensure the parent folder (which contains version_control.py) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
