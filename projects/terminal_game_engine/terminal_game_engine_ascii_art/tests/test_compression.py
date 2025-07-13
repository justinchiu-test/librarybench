"""Tests for compression system"""

import pytest
import json
import os
from pytermgame.compression import (
    SpriteCompressor, CompressedSprite, CompressionStats,
    Pattern, ColorPalette
)
from pytermgame.sprites import Sprite, Layer, Pixel, Color


class TestColorPalette:
    """Test ColorPalette functionality"""
    
    def test_palette_creation(self):
        """Test palette initialization"""
        palette = ColorPalette()
        
        assert len(palette.colors) == 0
        assert len(palette.indices) == 0
    
    def test_color_addition(self):
        """Test adding colors to palette"""
        palette = ColorPalette()
        
        color1 = Color(r=255, g=0, b=0)
        idx1 = palette.add_color(color1)
        assert idx1 == 0
        assert len(palette.colors) == 1
        
        color2 = Color(r=0, g=255, b=0)
        idx2 = palette.add_color(color2)
        assert idx2 == 1
        assert len(palette.colors) == 2
        
        # Same color should return existing index
        idx3 = palette.add_color(color1)
        assert idx3 == 0
        assert len(palette.colors) == 2
    
    def test_color_retrieval(self):
        """Test getting colors by index"""
        palette = ColorPalette()
        
        color = Color(r=128, g=64, b=255, a=0.5)
        idx = palette.add_color(color)
        
        retrieved = palette.get_color(idx)
        assert retrieved is not None
        assert retrieved.r == 128
        assert retrieved.g == 64
        assert retrieved.b == 255
        assert retrieved.a == 0.5
        
        # Invalid index
        assert palette.get_color(999) is None
    
    def test_index_lookup(self):
        """Test getting index for color"""
        palette = ColorPalette()
        
        color = Color(r=100, g=150, b=200)
        idx = palette.add_color(color)
        
        found_idx = palette.get_index(color)
        assert found_idx == idx
        
        # Non-existent color
        new_color = Color(r=1, g=2, b=3)
        assert palette.get_index(new_color) is None


class TestCompressedSprite:
    """Test CompressedSprite model"""
    
    def test_compressed_sprite_creation(self):
        """Test compressed sprite initialization"""
        compressed = CompressedSprite(
            name="Test",
            width=100,
            height=100
        )
        
        assert compressed.name == "Test"
        assert compressed.width == 100
        assert compressed.height == 100
        assert isinstance(compressed.palette, ColorPalette)
        assert isinstance(compressed.compression_stats, CompressionStats)


class TestSpriteCompressor:
    """Test sprite compression functionality"""
    
    def test_compressor_creation(self):
        """Test compressor initialization"""
        compressor = SpriteCompressor()
        
        assert compressor.min_pattern_size == 3
        assert compressor.max_pattern_size == 10
        assert compressor.min_pattern_frequency == 3
    
    def test_basic_compression(self):
        """Test basic sprite compression"""
        sprite = Sprite(name="Test", width=10, height=10)
        layer = sprite.add_layer("Layer1")
        
        # Add some pixels
        color1 = Color(r=255, g=0, b=0)
        color2 = Color(r=0, g=255, b=0)
        
        for i in range(5):
            layer.set_pixel(i, 0, Pixel(char='#', color=color1))
            layer.set_pixel(i, 1, Pixel(char='*', color=color2))
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        
        assert compressed.name == "Test"
        assert compressed.width == 10
        assert compressed.height == 10
        assert len(compressed.palette.colors) == 2
        assert compressed.compression_stats.unique_colors == 2
    
    def test_compression_decompression(self):
        """Test round-trip compression and decompression"""
        # Create sprite with pattern
        sprite = Sprite(name="Test", width=20, height=20)
        layer = sprite.add_layer("Pattern")
        
        # Create repeating pattern
        colors = [
            Color(r=255, g=0, b=0),
            Color(r=0, g=255, b=0),
            Color(r=0, g=0, b=255)
        ]
        
        for y in range(20):
            for x in range(20):
                color_idx = (x + y) % 3
                char = ['#', '*', '+'][color_idx]
                layer.set_pixel(x, y, Pixel(char=char, color=colors[color_idx]))
        
        # Compress and decompress
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        decompressed = compressor.decompress(compressed)
        
        # Verify sprite properties
        assert decompressed.name == sprite.name
        assert decompressed.width == sprite.width
        assert decompressed.height == sprite.height
        assert len(decompressed.layers) == len(sprite.layers)
        
        # Verify pixel data
        orig_layer = sprite.layers[0]
        decomp_layer = decompressed.layers[0]
        
        for y in range(20):
            for x in range(20):
                orig_pixel = orig_layer.get_pixel(x, y)
                decomp_pixel = decomp_layer.get_pixel(x, y)
                
                if orig_pixel:
                    assert decomp_pixel is not None
                    assert decomp_pixel.char == orig_pixel.char
                    assert decomp_pixel.color.r == orig_pixel.color.r
                    assert decomp_pixel.color.g == orig_pixel.color.g
                    assert decomp_pixel.color.b == orig_pixel.color.b
                else:
                    assert decomp_pixel is None
    
    def test_empty_sprite_compression(self):
        """Test compressing empty sprite"""
        sprite = Sprite(name="Empty", width=50, height=50)
        sprite.add_layer("Empty Layer")
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        
        assert compressed.compression_stats.unique_chars == 0
        assert compressed.compression_stats.unique_colors == 0
        
        # Decompress
        decompressed = compressor.decompress(compressed)
        assert len(decompressed.layers) == 1
        
        # All pixels should be None
        layer = decompressed.layers[0]
        for y in range(50):
            for x in range(50):
                assert layer.get_pixel(x, y) is None
    
    def test_run_length_encoding(self):
        """Test run-length encoding efficiency"""
        sprite = Sprite(name="RLE", width=100, height=1)
        layer = sprite.add_layer("Line")
        
        # Create long run of same pixel
        pixel = Pixel(char='=', color=Color(r=255, g=255, b=255))
        for x in range(100):
            layer.set_pixel(x, 0, pixel)
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        
        # Should have good compression ratio
        assert compressed.compression_stats.compression_ratio < 0.5
    
    def test_pattern_detection(self):
        """Test pattern detection in compression"""
        sprite = Sprite(name="Patterns", width=30, height=30)
        layer = sprite.add_layer("Pattern Layer")
        
        # Create 3x3 repeated pattern
        pattern = [
            ['#', '*', '#'],
            ['*', '#', '*'],
            ['#', '*', '#']
        ]
        
        color = Color(r=255, g=255, b=255)
        
        for py in range(0, 30, 3):
            for px in range(0, 30, 3):
                for dy in range(3):
                    for dx in range(3):
                        if py + dy < 30 and px + dx < 30:
                            char = pattern[dy][dx]
                            layer.set_pixel(px + dx, py + dy, 
                                          Pixel(char=char, color=color))
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        
        # Should detect patterns
        assert compressed.compression_stats.pattern_count > 0
    
    def test_multi_layer_compression(self):
        """Test compressing sprite with multiple layers"""
        sprite = Sprite(name="MultiLayer", width=20, height=20)
        
        # Add multiple layers with different content
        for i in range(3):
            layer = sprite.add_layer(f"Layer{i}")
            color = Color(r=255 if i == 0 else 0,
                         g=255 if i == 1 else 0,
                         b=255 if i == 2 else 0)
            
            for y in range(5):
                for x in range(5):
                    layer.set_pixel(x + i * 5, y + i * 5, 
                                   Pixel(char=str(i), color=color))
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        decompressed = compressor.decompress(compressed)
        
        # Verify all layers
        assert len(decompressed.layers) == 3
        
        for i, layer in enumerate(decompressed.layers):
            assert layer.name == f"Layer{i}"
            pixel = layer.get_pixel(i * 5, i * 5)
            assert pixel is not None
            assert pixel.char == str(i)
    
    def test_compression_stats(self):
        """Test compression statistics calculation"""
        sprite = Sprite(name="Stats", width=50, height=50)
        layer = sprite.add_layer("Content")
        
        # Add varied content
        chars = ['#', '*', '+', '-', '|']
        colors = [
            Color(r=255, g=0, b=0),
            Color(r=0, g=255, b=0),
            Color(r=0, g=0, b=255)
        ]
        
        for y in range(25):
            for x in range(25):
                char = chars[(x + y) % len(chars)]
                color = colors[(x * y) % len(colors)]
                layer.set_pixel(x, y, Pixel(char=char, color=color))
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        stats = compressed.compression_stats
        
        assert stats.original_size > 0
        assert stats.compressed_size > 0
        assert stats.compression_ratio > 0
        assert stats.unique_chars == len(chars)
        assert stats.unique_colors == len(colors)
    
    def test_file_operations(self):
        """Test saving and loading compressed sprites"""
        import tempfile
        
        # Create sprite
        sprite = Sprite(name="FileTest", width=30, height=30)
        layer = sprite.add_layer("Test")
        
        for i in range(10):
            layer.set_pixel(i, i, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        
        compressor = SpriteCompressor()
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            stats = compressor.compress_to_file(sprite, filepath)
            assert stats.original_size > 0
            
            # Load from file
            loaded = compressor.decompress_from_file(filepath)
            
            assert loaded.name == "FileTest"
            assert loaded.width == 30
            assert loaded.height == 30
            
            # Verify content
            loaded_pixel = loaded.layers[0].get_pixel(5, 5)
            assert loaded_pixel is not None
            assert loaded_pixel.char == '#'
            
        finally:
            os.unlink(filepath)
    
    def test_compression_ratio_estimation(self):
        """Test compression ratio estimation"""
        compressor = SpriteCompressor()
        
        # Empty sprite - worst case
        empty_sprite = Sprite(name="Empty", width=100, height=100)
        empty_sprite.add_layer("Empty")
        
        ratio = compressor.estimate_compression_ratio(empty_sprite)
        assert ratio == 1.0  # No compression possible
        
        # Full sprite with variety
        full_sprite = Sprite(name="Full", width=50, height=50)
        layer = full_sprite.add_layer("Content")
        
        for y in range(50):
            for x in range(50):
                char = chr(65 + ((x + y) % 26))
                color = Color(
                    r=(x * 5) % 256,
                    g=(y * 5) % 256,
                    b=((x + y) * 5) % 256
                )
                layer.set_pixel(x, y, Pixel(char=char, color=color))
        
        ratio = compressor.estimate_compression_ratio(full_sprite)
        assert 0.0 < ratio < 1.0
        
        # Uniform sprite - best case
        uniform_sprite = Sprite(name="Uniform", width=100, height=100)
        layer = uniform_sprite.add_layer("Uniform")
        
        pixel = Pixel(char='#', color=Color(r=255, g=255, b=255))
        for y in range(100):
            for x in range(100):
                layer.set_pixel(x, y, pixel)
        
        ratio = compressor.estimate_compression_ratio(uniform_sprite)
        assert ratio < 0.3  # Should compress well
    
    def test_layer_properties_preservation(self):
        """Test that layer properties are preserved"""
        sprite = Sprite(name="Properties", width=20, height=20)
        
        layer = sprite.add_layer("TestLayer")
        layer.visible = False
        layer.opacity = 0.7
        layer.blend_mode = "add"
        
        # Add some content
        layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=255, g=0, b=0)))
        
        compressor = SpriteCompressor()
        compressed = compressor.compress(sprite)
        decompressed = compressor.decompress(compressed)
        
        # Check layer properties
        decomp_layer = decompressed.layers[0]
        assert decomp_layer.name == "TestLayer"
        assert decomp_layer.visible is False
        assert decomp_layer.opacity == 0.7
        assert decomp_layer.blend_mode == "add"