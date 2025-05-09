from guidelines import unit_tests

def test_unit_tests_outline():
    outline = unit_tests()
    # Primitives
    assert "encoding of primitives" in outline.lower()
    assert "decoding of primitives" in outline.lower()
    # Lists
    assert "lists" in outline.lower()
    # Dictionaries
    assert "dictionaries" in outline.lower()
    # Nested
    assert "nested structures" in outline.lower()
    # Invalid inputs
    assert "invalid inputs" in outline.lower()
    # pytest mention
    assert "pytest" in outline.lower()
