"""Adapter for data_scientist.datapipeline_cli.di."""

from ....cli_core.di import DIContainer, init_di, inject

# Re-export the classes and functions for backward compatibility

__all__ = ['DIContainer', 'init_di', 'inject']
