import sys
import os
# add src directory to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
import pytest

@pytest.fixture
def tmp_env(monkeypatch):
    """Temporary environment fixture."""
    # Provide isolated environment for tests that expect tmp_env
    # No-op; monkeypatch will handle env changes in tests
    yield