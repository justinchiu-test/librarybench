"""Adapter for data_scientist.datapipeline_cli.signals."""

import signal
from ....cli_core.signals import register_handler, unregister_handler, reset_handlers

# Re-export the functions for backward compatibility
