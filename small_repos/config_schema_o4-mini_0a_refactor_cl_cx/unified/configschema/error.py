"""
Custom exceptions for configuration validation and processing.
"""

class ValidationError(Exception):
    """
    Exception raised for validation errors in configuration.
    """
    def __init__(
        self,
        file=None,
        line=None,
        section=None,
        key=None,
        message="",
        suggestions=None,
        expected=None,
        actual=None
    ):
        self.file = file
        self.line = line
        self.section = section
        self.key = key
        self.message = message
        self.suggestions = suggestions or []
        self.expected = expected
        self.actual = actual
        super().__init__(self.message)

    def __str__(self):
        parts = []
        if self.file is not None:
            parts.append(f"File '{self.file}'")
        if self.line is not None:
            parts.append(f"Line {self.line}")
        if self.section is not None:
            parts.append(f"In section '{self.section}'")
        if self.key is not None:
            parts.append(f"Key '{self.key}'")
        if self.message:
            parts.append(self.message)
        if self.expected is not None:
            parts.append(f"expected {self.expected}")
        if self.actual is not None:
            parts.append(f"actual {self.actual}")
        if self.suggestions:
            parts.append(f"Suggestions: {', '.join(self.suggestions)}")
        return "; ".join(parts)