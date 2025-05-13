import pytest
from config_watcher.diffs import generate_diff

def test_generate_diff_content():
    old = "line1\nline2\n"
    new = "line1\nline2 modified\nline3\n"
    diff = generate_diff(old, new, 'old', 'new')
    assert '-line2\n' in diff
    assert '+line2 modified\n' in diff
    assert '+line3\n' in diff
