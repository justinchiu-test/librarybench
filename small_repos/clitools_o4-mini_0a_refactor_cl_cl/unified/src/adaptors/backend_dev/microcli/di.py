"""
Backend developer DI adapter.

Provides backward compatibility for backend_dev.microcli.di.
"""

from ....cli_core.di import DIContainer, init_di


# Re-export init_di for backward compatibility
# This ensures the tests can use this function as before