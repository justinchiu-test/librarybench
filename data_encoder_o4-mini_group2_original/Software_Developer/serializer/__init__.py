"""
serializer: A small cross‐platform serialization library with support for
custom types, decoding configurations (e.g. lazy lists), and
cross‐language JSON output.
"""

from .serializer import (
    custom_type_support,
    encoding,
    decoding,
    cross_language_support,
)
from .config import decoding_settings, decoding_configuration
from .lazy import LazyList

__all__ = [
    "custom_type_support",
    "encoding",
    "decoding",
    "cross_language_support",
    "decoding_settings",
    "decoding_configuration",
    "LazyList",
]
