import os as _os
import time as _time
import tempfile
import shutil
from pathlib import Path
import pytest

@pytest.fixture
def os():
    return _os

@pytest.fixture
def time():
    return _time

@pytest.fixture(scope='module')
def tmp_path():
    # Provide a module-scoped tmp_path fixture to satisfy module-scoped server fixture
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(str(path))
