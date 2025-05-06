def contribute_guidelines():
    """
    Returns a string containing guidelines for contributing to this project.
    """
    return """Contribution Guidelines
======================

1. Fork the repository:
   - Click the 'Fork' button at the top-right corner of the repo.
2. Create a descriptive branch:
   - Use a branch name like feature/your-feature or fix/issue-description.
3. Follow coding style:
   - Stick to PEP8 conventions.
   - Write clear, concise code with comments where necessary.
4. Write unit tests:
   - Ensure new functionality is covered.
   - Run tests with pytest and aim for high coverage.
5. Commit messages:
   - Use present-tense verbs, e.g., "Add feature X" or "Fix bug Y".
   - Reference issue numbers when applicable.
6. Submit a Pull Request:
   - Describe the change, why it's needed, and any trade-offs.
   - Link related issues and tag maintainers for review.
7. Respond to feedback:
   - Be open to suggestions and update your PR accordingly.
"""

def unit_tests():
    """
    Returns a string outlining the suite of unit tests for encoding/decoding.
    """
    return """Unit Testing Suite Outline
==========================

- Test encoding of primitives:
  * Integers, floats, booleans, and strings should encode correctly.
- Test decoding of primitives:
  * Valid JSON strings map back to original values.
- Test encoding/decoding of lists:
  * Homogeneous and heterogeneous lists, including empty lists.
- Test encoding/decoding of dictionaries:
  * Including nested dicts, string keys, and various value types.
- Test nested structures:
  * Deeply nested combinations of lists and dicts.
- Test invalid inputs:
  * decode() should raise an error on malformed JSON.
- Use pytest for all tests.
"""
