"""
Configuration for pytest.

This file ensures that the correct import paths are available for tests.
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))