import builtins
import pytest

# Expose pytest in the builtins so that test modules referencing pytest
# without importing it will find it.
builtins.pytest = pytest

from .plugin import Plugin
