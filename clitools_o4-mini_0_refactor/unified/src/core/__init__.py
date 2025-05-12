"""
Core infrastructure modules: config management, DI, i18n, signal handling.
"""
from .config import parser, schema, validator, loader
from .di import init_di, Container, inject
from .i18n import load_translations
from .signals import handle_signals, _get_registered_signals