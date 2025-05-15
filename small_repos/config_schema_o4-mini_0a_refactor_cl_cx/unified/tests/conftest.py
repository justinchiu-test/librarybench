# Add project root to sys.path so that configschema package can be imported
import sys
import os

# Insert the parent directory of tests/ into sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))