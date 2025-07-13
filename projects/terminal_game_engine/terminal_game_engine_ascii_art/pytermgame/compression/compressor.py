"""ASCII art compression for efficient sprite storage"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field
import zlib
import base64
import json
from collections import Counter

from ..sprites.models import Sprite, Layer, Pixel, Color


class CompressionStats(BaseModel):
    """Compression statistics"""
    
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    pattern_count: int = 0
    unique_chars: int = 0
    unique_colors: int = 0


class Pattern(BaseModel):
    """Repeated pattern in sprite data"""
    
    data: str
    positions: List[Tuple[int, int]]
    width: int
    height: int
    frequency: int = 0


class ColorPalette(BaseModel):
    """Optimized color palette"""
    
    colors: List[Color] = Field(default_factory=list)
    indices: Dict[str, int] = Field(default_factory=dict)
    
    def add_color(self, color: Color) -> int:
        """Add color to palette and return index"""
        color_key = f"{color.r},{color.g},{color.b},{color.a}"
        
        if color_key in self.indices:
            return self.indices[color_key]
        
        index = len(self.colors)
        self.colors.append(color)
        self.indices[color_key] = index
        return index
    
    def get_color(self, index: int) -> Optional[Color]:
        """Get color by index"""
        if 0 <= index < len(self.colors):
            return self.colors[index]
        return None
    
    def get_index(self, color: Color) -> Optional[int]:
        """Get index for color"""
        color_key = f"{color.r},{color.g},{color.b},{color.a}"
        return self.indices.get(color_key)


class CompressedSprite(BaseModel):
    """Compressed sprite data"""
    
    name: str
    width: int
    height: int
    layers: List[Dict[str, Any]] = Field(default_factory=list)
    palette: ColorPalette = Field(default_factory=ColorPalette)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    compression_stats: CompressionStats = Field(default_factory=CompressionStats)


class SpriteCompressor:
    """Compress and decompress ASCII sprites"""
    
    def __init__(self):
        self.min_pattern_size = 3
        self.max_pattern_size = 10
        self.min_pattern_frequency = 3
    
    def compress(self, sprite: Sprite) -> CompressedSprite:
        """Compress sprite data"""
        compressed = CompressedSprite(
            name=sprite.name,
            width=sprite.width,
            height=sprite.height,
            metadata=sprite.metadata
        )
        
        original_size = 0
        
        # Build color palette
        for layer in sprite.layers:
            for row in layer.pixels:
                for pixel in row:
                    if pixel:
                        compressed.palette.add_color(pixel.color)
                        original_size += len(pixel.char) + 12  # Rough size estimate
        
        # Compress each layer
        for layer in sprite.layers:
            compressed_layer = self._compress_layer(layer, compressed.palette)
            compressed.layers.append(compressed_layer)
        
        # Calculate compression stats
        compressed_data = json.dumps(compressed.model_dump())
        compressed_size = len(compressed_data.encode())
        
        compressed.compression_stats = CompressionStats(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compressed_size / original_size if original_size > 0 else 1.0,
            unique_chars=self._count_unique_chars(sprite),
            unique_colors=len(compressed.palette.colors)
        )
        
        return compressed
    
    def decompress(self, compressed: CompressedSprite) -> Sprite:
        """Decompress sprite data"""
        sprite = Sprite(
            name=compressed.name,
            width=compressed.width,
            height=compressed.height,
            metadata=compressed.metadata
        )
        
        # Decompress each layer
        for compressed_layer in compressed.layers:
            layer = self._decompress_layer(compressed_layer, compressed.palette, 
                                          compressed.width, compressed.height)
            sprite.layers.append(layer)
        
        return sprite
    
    def _compress_layer(self, layer: Layer, palette: ColorPalette) -> Dict[str, Any]:
        """Compress single layer"""
        # Convert pixels to run-length encoded format
        runs = []
        current_run = None
        
        for y in range(layer.height):
            for x in range(layer.width):
                pixel = layer.pixels[y][x]
                
                if pixel:
                    color_idx = palette.get_index(pixel.color)
                    pixel_data = (pixel.char, color_idx)
                else:
                    pixel_data = None
                
                if current_run is None:
                    current_run = [pixel_data, 1]
                elif current_run[0] == pixel_data:
                    current_run[1] += 1
                else:
                    runs.append(current_run)
                    current_run = [pixel_data, 1]
        
        if current_run:
            runs.append(current_run)
        
        # Find repeated patterns
        patterns = self._find_patterns(layer)
        
        # Encode layer data
        layer_data = {
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode,
            "runs": runs,
            "patterns": [p.model_dump() for p in patterns]
        }
        
        # Further compress with zlib
        encoded = json.dumps(layer_data)
        compressed = zlib.compress(encoded.encode())
        layer_data["compressed"] = base64.b64encode(compressed).decode()
        
        return layer_data
    
    def _decompress_layer(self, compressed_layer: Dict[str, Any], 
                         palette: ColorPalette, width: int, height: int) -> Layer:
        """Decompress single layer"""
        # Decompress if needed
        if "compressed" in compressed_layer:
            compressed_data = base64.b64decode(compressed_layer["compressed"])
            decompressed = zlib.decompress(compressed_data)
            layer_data = json.loads(decompressed.decode())
        else:
            layer_data = compressed_layer
        
        layer = Layer(
            name=layer_data["name"],
            width=width,
            height=height,
            visible=layer_data.get("visible", True),
            opacity=layer_data.get("opacity", 1.0),
            blend_mode=layer_data.get("blend_mode", "normal")
        )
        
        # Decode run-length encoded data
        pixel_index = 0
        for run in layer_data["runs"]:
            pixel_data, count = run
            
            for _ in range(count):
                y = pixel_index // width
                x = pixel_index % width
                
                if pixel_data:
                    char, color_idx = pixel_data
                    color = palette.get_color(color_idx)
                    if color:
                        layer.pixels[y][x] = Pixel(char=char, color=color)
                
                pixel_index += 1
        
        return layer
    
    def _find_patterns(self, layer: Layer) -> List[Pattern]:
        """Find repeated patterns in layer"""
        patterns = []
        pattern_map = {}
        
        # Search for rectangular patterns
        for h in range(self.min_pattern_size, min(self.max_pattern_size, layer.height) + 1):
            for w in range(self.min_pattern_size, min(self.max_pattern_size, layer.width) + 1):
                
                for y in range(layer.height - h + 1):
                    for x in range(layer.width - w + 1):
                        # Extract pattern
                        pattern_data = self._extract_pattern(layer, x, y, w, h)
                        
                        if pattern_data not in pattern_map:
                            pattern_map[pattern_data] = Pattern(
                                data=pattern_data,
                                positions=[],
                                width=w,
                                height=h
                            )
                        
                        pattern_map[pattern_data].positions.append((x, y))
                        pattern_map[pattern_data].frequency += 1
        
        # Filter patterns by frequency
        for pattern in pattern_map.values():
            if pattern.frequency >= self.min_pattern_frequency:
                patterns.append(pattern)
        
        return patterns
    
    def _extract_pattern(self, layer: Layer, x: int, y: int, 
                        width: int, height: int) -> str:
        """Extract pattern data as string"""
        pattern_chars = []
        
        for dy in range(height):
            for dx in range(width):
                pixel = layer.pixels[y + dy][x + dx]
                if pixel:
                    pattern_chars.append(f"{pixel.char},{pixel.color.r},{pixel.color.g},{pixel.color.b}")
                else:
                    pattern_chars.append("_")
        
        return "|".join(pattern_chars)
    
    def _count_unique_chars(self, sprite: Sprite) -> int:
        """Count unique characters in sprite"""
        chars = set()
        
        for layer in sprite.layers:
            for row in layer.pixels:
                for pixel in row:
                    if pixel:
                        chars.add(pixel.char)
        
        return len(chars)
    
    def compress_to_file(self, sprite: Sprite, filepath: str) -> CompressionStats:
        """Compress sprite to file"""
        compressed = self.compress(sprite)
        
        with open(filepath, 'w') as f:
            json.dump(compressed.model_dump(), f)
        
        return compressed.compression_stats
    
    def decompress_from_file(self, filepath: str) -> Sprite:
        """Decompress sprite from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        compressed = CompressedSprite(**data)
        return self.decompress(compressed)
    
    def estimate_compression_ratio(self, sprite: Sprite) -> float:
        """Estimate compression ratio without full compression"""
        # Count unique elements
        unique_chars = self._count_unique_chars(sprite)
        unique_colors = set()
        total_pixels = 0
        empty_pixels = 0
        
        for layer in sprite.layers:
            for row in layer.pixels:
                for pixel in row:
                    total_pixels += 1
                    if pixel:
                        unique_colors.add((pixel.color.r, pixel.color.g, pixel.color.b))
                    else:
                        empty_pixels += 1
        
        # Estimate based on entropy
        if total_pixels == 0:
            return 1.0
        
        fill_ratio = 1.0 - (empty_pixels / total_pixels)
        color_ratio = len(unique_colors) / max(1, total_pixels * fill_ratio)
        char_ratio = unique_chars / max(1, total_pixels * fill_ratio)
        
        # Rough estimate of compression ratio
        estimated_ratio = 0.1 + (0.9 * fill_ratio * color_ratio * char_ratio)
        
        return min(1.0, estimated_ratio)