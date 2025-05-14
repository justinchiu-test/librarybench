"""
Translator cache adapter.

Provides backward compatibility for translator.cache.
"""

from ...utils.cache import Cache


# Re-export the Cache class for backward compatibility
# This ensures the tests can use this class as before