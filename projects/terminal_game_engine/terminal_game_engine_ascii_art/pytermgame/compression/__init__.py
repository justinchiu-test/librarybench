"""Compression module exports"""

from .compressor import (
    SpriteCompressor, CompressedSprite, CompressionStats,
    Pattern, ColorPalette
)

__all__ = [
    'SpriteCompressor', 'CompressedSprite', 'CompressionStats',
    'Pattern', 'ColorPalette'
]