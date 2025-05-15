#!/usr/bin/env python3
"""
Command-line script for the unified task manager.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.main import main

if __name__ == "__main__":
    sys.exit(main())