"""
Optimization utilities for the common library.

This package provides optimization components such as compression, caching,
and batching, which can be used by both vectordb and syncdb implementations.
"""

from .compression import (
    compress_string,
    decompress_string,
    compress_bytes,
    decompress_bytes,
    compress_json,
    decompress_json,
    TYPE_COMPRESSORS,
    TypeAwareCompressor
)

__all__ = [
    # Compression utilities
    "compress_string",
    "decompress_string",
    "compress_bytes",
    "decompress_bytes",
    "compress_json",
    "decompress_json",
    "TYPE_COMPRESSORS",
    "TypeAwareCompressor"
]