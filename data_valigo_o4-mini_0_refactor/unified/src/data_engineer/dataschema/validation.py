"""
Facade for async rule validation for Data Engineer.
"""
import asyncio
from data_engineer.dataschema.validation import AsyncRule as _AsyncRule

class AsyncRule(_AsyncRule):
    """
    Wrapper around original AsyncRule to ensure validate() works in all contexts.
    """
    def validate(self, *args, **kwargs):
        try:
            return super().validate(*args, **kwargs)
        except RuntimeError:
            # Fallback to running async validation in new loop
            return asyncio.run(self.validate_async(*args, **kwargs))

__all__ = ['AsyncRule']