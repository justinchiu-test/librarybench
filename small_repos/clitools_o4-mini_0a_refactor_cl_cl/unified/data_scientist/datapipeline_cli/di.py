"""Dependency injection for data scientist CLI tools."""

from src.cli_core.di import DIContainer, init_di, inject

__all__ = ['DIContainer', 'init_di', 'inject']