import sys, os
# Debug sys.path for pytest
print("PYTEST SYSPATH:", sys.path)

# Add the project root (two levels up) to sys.path so pytest can import original modules
# Determine paths for unified root and project root
here = os.path.abspath(os.path.dirname(__file__))
unified_root = os.path.abspath(os.path.join(here, '..'))
project_root = os.path.abspath(os.path.join(unified_root, '..'))
# Ensure unified root has highest priority for imports
if unified_root not in sys.path:
    sys.path.insert(0, unified_root)
# Remove project root from sys.path to prevent importing original code
# Remove project root from sys.path to prevent importing original code
if project_root in sys.path:
    sys.path.remove(project_root)
# Debug sys.path after modifications
print("PYTEST POST-SYSPATH:", sys.path)