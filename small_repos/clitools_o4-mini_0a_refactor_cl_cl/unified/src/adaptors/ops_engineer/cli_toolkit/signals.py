"""Adapter for ops_engineer.cli_toolkit.signals."""

import signal
from ....cli_core.signals import register_handler, unregister_handler, reset_handlers

# Re-export the functions for backward compatibility
