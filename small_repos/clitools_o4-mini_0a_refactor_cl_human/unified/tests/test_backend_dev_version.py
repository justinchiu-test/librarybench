import pytest
from src.core.dev.version import Version, VersionComponent

def test_bump_normal():
    # Create a version
    v = Version(1, 2, 3)
    
    # Bump patch version
    v.bump(VersionComponent.PATCH)
    
    # Verify
    assert str(v) == "1.2.4"

def test_bump_minor():
    # Create a version
    v = Version(1, 2, 3)
    
    # Bump minor version
    v.bump(VersionComponent.MINOR)
    
    # Verify minor is incremented and patch is reset
    assert str(v) == "1.3.0"

def test_bump_major():
    # Create a version
    v = Version(1, 2, 3)
    
    # Bump major version
    v.bump(VersionComponent.MAJOR)
    
    # Verify major is incremented and minor/patch are reset
    assert str(v) == "2.0.0"

def test_version_parsing():
    # Parse a version string
    v = Version.parse("1.2.3")
    
    # Verify components
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3

def test_invalid_format():
    # Try to parse an invalid version string
    with pytest.raises(ValueError):
        Version.parse("a.b.c")