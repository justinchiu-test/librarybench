# deprecation_warnings
import warnings

class DeprecationManager:
    def __init__(self):
        self._deprecated = {}

    def mark(self, key: str, message: str = None):
        """
        Mark a config key as deprecated with an optional message.
        """
        self._deprecated[key] = message or f"'{key}' is deprecated."

    def warn_if_deprecated(self, key: str):
        """
        If key is deprecated, emit a warning.
        """
        if key in self._deprecated:
            warnings.warn(self._deprecated[key], DeprecationWarning)
