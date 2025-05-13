# allow tests to find ./filewatcher as a top‐level package
import os, sys

# project‐root is the directory containing *this* file
_project_root = os.path.dirname(__file__)

# make sure pytest (which adds the project‐root to sys.path) can see ./filewatcher
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
