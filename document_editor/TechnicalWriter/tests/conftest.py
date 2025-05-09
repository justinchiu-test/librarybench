import os
import sys

# Ensure the parent directory (where doc_manager.py lives)
# is on sys.path so that `import doc_manager` works.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
