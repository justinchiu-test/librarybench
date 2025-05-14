"""Adapter for data_scientist.datapipeline_cli.help_formatter."""

from ....cli_core.help_formatter import ColoredHelpFormatter, create_help_formatter, format_help

# Re-export the classes and functions for backward compatibility
__all__ = ['ColoredHelpFormatter', 'create_help_formatter', 'format_help']
