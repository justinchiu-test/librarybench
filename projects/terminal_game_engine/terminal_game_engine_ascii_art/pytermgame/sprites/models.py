"""Sprite models and data structures"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field, field_validator
import numpy as np


class Color(BaseModel):
    """ASCII color representation"""
    
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)
    a: float = Field(ge=0.0, le=1.0, default=1.0)
    
    def to_ansi(self) -> str:
        """Convert to ANSI color code"""
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def blend(self, other: 'Color', alpha: float) -> 'Color':
        """Blend with another color"""
        inv_alpha = 1.0 - alpha
        return Color(
            r=int(self.r * inv_alpha + other.r * alpha),
            g=int(self.g * inv_alpha + other.g * alpha),
            b=int(self.b * inv_alpha + other.b * alpha),
            a=self.a * inv_alpha + other.a * alpha
        )


class Pixel(BaseModel):
    """Single ASCII pixel with character and color"""
    
    char: str = Field(default=' ', max_length=1)
    color: Color = Field(default_factory=lambda: Color(r=255, g=255, b=255))
    background: Optional[Color] = None
    
    @field_validator('char')
    def validate_char(cls, v: str) -> str:
        if len(v) != 1:
            raise ValueError("Character must be exactly one character")
        return v


class Layer(BaseModel):
    """Single layer in a sprite"""
    
    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    pixels: List[List[Optional[Pixel]]] = Field(default_factory=list)
    visible: bool = True
    opacity: float = Field(ge=0.0, le=1.0, default=1.0)
    blend_mode: str = Field(default="normal")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.pixels:
            self.pixels = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def get_pixel(self, x: int, y: int) -> Optional[Pixel]:
        """Get pixel at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None
    
    def set_pixel(self, x: int, y: int, pixel: Optional[Pixel]) -> None:
        """Set pixel at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = pixel
    
    def clear(self) -> None:
        """Clear all pixels"""
        self.pixels = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def resize(self, width: int, height: int) -> None:
        """Resize layer"""
        new_pixels = [[None for _ in range(width)] for _ in range(height)]
        
        for y in range(min(height, self.height)):
            for x in range(min(width, self.width)):
                new_pixels[y][x] = self.pixels[y][x]
        
        self.width = width
        self.height = height
        self.pixels = new_pixels


class Sprite(BaseModel):
    """Multi-layer ASCII sprite"""
    
    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    layers: List[Layer] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_layer(self, name: str, index: Optional[int] = None) -> Layer:
        """Add a new layer"""
        layer = Layer(name=name, width=self.width, height=self.height)
        if index is not None:
            self.layers.insert(index, layer)
        else:
            self.layers.append(layer)
        return layer
    
    def remove_layer(self, index: int) -> None:
        """Remove layer by index"""
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
    
    def get_layer(self, name: str) -> Optional[Layer]:
        """Get layer by name"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
    
    def move_layer(self, from_index: int, to_index: int) -> None:
        """Move layer to new position"""
        if 0 <= from_index < len(self.layers) and 0 <= to_index < len(self.layers):
            layer = self.layers.pop(from_index)
            self.layers.insert(to_index, layer)
    
    def composite(self) -> List[List[Optional[Pixel]]]:
        """Composite all visible layers"""
        result = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        for layer in self.layers:
            if not layer.visible:
                continue
                
            for y in range(self.height):
                for x in range(self.width):
                    src_pixel = layer.get_pixel(x, y)
                    if src_pixel is None:
                        continue
                    
                    if result[y][x] is None:
                        result[y][x] = src_pixel
                    else:
                        # Blend pixels based on opacity
                        dst_pixel = result[y][x]
                        alpha = layer.opacity * src_pixel.color.a
                        
                        if layer.blend_mode == "normal":
                            blended_color = dst_pixel.color.blend(src_pixel.color, alpha)
                            result[y][x] = Pixel(
                                char=src_pixel.char if alpha > 0.5 else dst_pixel.char,
                                color=blended_color
                            )
        
        return result


class Palette(BaseModel):
    """Color palette for sprite editing"""
    
    name: str
    colors: List[Color] = Field(default_factory=list)
    
    def add_color(self, color: Color) -> None:
        """Add color to palette"""
        if color not in self.colors:
            self.colors.append(color)
    
    def remove_color(self, index: int) -> None:
        """Remove color by index"""
        if 0 <= index < len(self.colors):
            self.colors.pop(index)