from guidelines import contribute_guidelines

def test_contribute_guidelines_contains_sections():
    text = contribute_guidelines()
    assert "Fork the repository" in text
    assert "Pull Request" in text
    # Check for coding style mention (case-insensitive)
    assert "coding style" in text.lower()
    # Ensure tests are mentioned
    assert "unit tests" in text.lower() or "tests" in text.lower()
