import os
import sys

# Ensure that the directory containing this conftest (and your modules)
# is on the PYTHONPATH so pytest can import encoding_configuration, etc.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
