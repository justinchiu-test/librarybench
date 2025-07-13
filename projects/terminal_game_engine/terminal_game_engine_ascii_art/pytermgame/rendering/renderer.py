"""Layered rendering system with transparency and effects"""

from typing import List, Tuple, Optional, Dict, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np

from ..sprites.models import Pixel, Color, Layer, Sprite


class BlendMode(str, Enum):
    """Blend modes for layer composition"""
    
    NORMAL = "normal"
    ADD = "add"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    DIFFERENCE = "difference"


class RenderLayer(BaseModel):
    """Render layer with effects"""
    
    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    pixels: List[List[Optional[Pixel]]] = Field(default_factory=list)
    z_order: int = 0
    visible: bool = True
    opacity: float = Field(ge=0.0, le=1.0, default=1.0)
    blend_mode: BlendMode = BlendMode.NORMAL
    offset_x: int = 0
    offset_y: int = 0
    effects: List[str] = Field(default_factory=list)
    
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
    
    def clear(self, color: Optional[Color] = None) -> None:
        """Clear layer with optional color"""
        if color:
            pixel = Pixel(char=' ', color=color)
            self.pixels = [[pixel for _ in range(self.width)] for _ in range(self.height)]
        else:
            self.pixels = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def copy_from_sprite_layer(self, layer: Layer) -> None:
        """Copy pixels from sprite layer"""
        self.width = layer.width
        self.height = layer.height
        self.pixels = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(min(self.height, layer.height)):
            for x in range(min(self.width, layer.width)):
                self.pixels[y][x] = layer.get_pixel(x, y)


class Viewport(BaseModel):
    """Rendering viewport"""
    
    x: int = 0
    y: int = 0
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is in viewport"""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        return (world_x - self.x, world_y - self.y)
    
    def to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        return (screen_x + self.x, screen_y + self.y)


class LayerEffect:
    """Base class for layer effects"""
    
    def apply(self, layer: RenderLayer) -> None:
        """Apply effect to layer"""
        pass


class BlurEffect(LayerEffect):
    """Simple blur effect"""
    
    def __init__(self, radius: int = 1):
        self.radius = radius
    
    def apply(self, layer: RenderLayer) -> None:
        """Apply blur to layer"""
        new_pixels = [[None for _ in range(layer.width)] for _ in range(layer.height)]
        
        for y in range(layer.height):
            for x in range(layer.width):
                # Sample surrounding pixels
                colors = []
                chars = []
                
                for dy in range(-self.radius, self.radius + 1):
                    for dx in range(-self.radius, self.radius + 1):
                        px = x + dx
                        py = y + dy
                        
                        if 0 <= px < layer.width and 0 <= py < layer.height:
                            pixel = layer.pixels[py][px]
                            if pixel:
                                colors.append(pixel.color)
                                chars.append(pixel.char)
                
                if colors:
                    # Average colors
                    avg_r = sum(c.r for c in colors) // len(colors)
                    avg_g = sum(c.g for c in colors) // len(colors)
                    avg_b = sum(c.b for c in colors) // len(colors)
                    avg_a = sum(c.a for c in colors) / len(colors)
                    
                    # Use most common char
                    char = max(set(chars), key=chars.count) if chars else ' '
                    
                    new_pixels[y][x] = Pixel(
                        char=char,
                        color=Color(r=avg_r, g=avg_g, b=avg_b, a=avg_a)
                    )
        
        layer.pixels = new_pixels


class GlowEffect(LayerEffect):
    """Glow effect"""
    
    def __init__(self, intensity: float = 1.5, radius: int = 2):
        self.intensity = intensity
        self.radius = radius
    
    def apply(self, layer: RenderLayer) -> None:
        """Apply glow to layer"""
        # Create glow layer
        glow_pixels = [[None for _ in range(layer.width)] for _ in range(layer.height)]
        
        for y in range(layer.height):
            for x in range(layer.width):
                pixel = layer.pixels[y][x]
                if pixel and pixel.color.a > 0:
                    # Spread glow around pixel
                    for dy in range(-self.radius, self.radius + 1):
                        for dx in range(-self.radius, self.radius + 1):
                            if dx == 0 and dy == 0:
                                continue
                                
                            px = x + dx
                            py = y + dy
                            
                            if 0 <= px < layer.width and 0 <= py < layer.height:
                                distance = (dx * dx + dy * dy) ** 0.5
                                glow_alpha = (1.0 - distance / self.radius) * 0.5
                                
                                if glow_alpha > 0:
                                    glow_color = Color(
                                        r=min(255, int(pixel.color.r * self.intensity)),
                                        g=min(255, int(pixel.color.g * self.intensity)),
                                        b=min(255, int(pixel.color.b * self.intensity)),
                                        a=glow_alpha * pixel.color.a
                                    )
                                    
                                    if glow_pixels[py][px] is None:
                                        glow_pixels[py][px] = Pixel(char=' ', color=glow_color)
                                    else:
                                        # Blend glows
                                        existing = glow_pixels[py][px].color
                                        glow_pixels[py][px].color = existing.blend(glow_color, glow_alpha)
        
        # Merge glow with original
        for y in range(layer.height):
            for x in range(layer.width):
                if glow_pixels[y][x] and layer.pixels[y][x] is None:
                    layer.pixels[y][x] = glow_pixels[y][x]


class Renderer:
    """Main rendering engine"""
    
    def __init__(self, width: int, height: int):
        """Initialize renderer"""
        self.width = width
        self.height = height
        self.layers: List[RenderLayer] = []
        self.viewport = Viewport(x=0, y=0, width=width, height=height)
        self.background_color = Color(r=0, g=0, b=0)
        self.effects: Dict[str, LayerEffect] = {
            "blur": BlurEffect(),
            "glow": GlowEffect(),
        }
    
    def add_layer(self, layer: RenderLayer) -> None:
        """Add render layer"""
        self.layers.append(layer)
        self._sort_layers()
    
    def remove_layer(self, name: str) -> None:
        """Remove layer by name"""
        self.layers = [l for l in self.layers if l.name != name]
    
    def get_layer(self, name: str) -> Optional[RenderLayer]:
        """Get layer by name"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
    
    def set_layer_z_order(self, name: str, z_order: int) -> None:
        """Set layer z-order"""
        layer = self.get_layer(name)
        if layer:
            layer.z_order = z_order
            self._sort_layers()
    
    def _sort_layers(self) -> None:
        """Sort layers by z-order"""
        self.layers.sort(key=lambda l: l.z_order)
    
    def _blend_pixels(self, bottom: Optional[Pixel], top: Optional[Pixel], 
                     opacity: float, blend_mode: BlendMode) -> Optional[Pixel]:
        """Blend two pixels"""
        if top is None:
            return bottom
        if bottom is None:
            return Pixel(char=top.char, color=Color(
                r=top.color.r, g=top.color.g, b=top.color.b,
                a=top.color.a * opacity
            ))
        
        # Apply blend mode
        if blend_mode == BlendMode.NORMAL:
            blended_color = bottom.color.blend(top.color, opacity * top.color.a)
        
        elif blend_mode == BlendMode.ADD:
            blended_color = Color(
                r=min(255, bottom.color.r + int(top.color.r * opacity)),
                g=min(255, bottom.color.g + int(top.color.g * opacity)),
                b=min(255, bottom.color.b + int(top.color.b * opacity)),
                a=min(1.0, bottom.color.a + top.color.a * opacity)
            )
        
        elif blend_mode == BlendMode.MULTIPLY:
            blended_color = Color(
                r=int((bottom.color.r * top.color.r * opacity) / 255),
                g=int((bottom.color.g * top.color.g * opacity) / 255),
                b=int((bottom.color.b * top.color.b * opacity) / 255),
                a=bottom.color.a * top.color.a * opacity
            )
        
        elif blend_mode == BlendMode.SCREEN:
            blended_color = Color(
                r=255 - int(((255 - bottom.color.r) * (255 - top.color.r * opacity)) / 255),
                g=255 - int(((255 - bottom.color.g) * (255 - top.color.g * opacity)) / 255),
                b=255 - int(((255 - bottom.color.b) * (255 - top.color.b * opacity)) / 255),
                a=1.0 - (1.0 - bottom.color.a) * (1.0 - top.color.a * opacity)
            )
        
        else:
            # Default to normal blending
            blended_color = bottom.color.blend(top.color, opacity * top.color.a)
        
        # Choose character based on opacity
        char = top.char if opacity * top.color.a > 0.5 else bottom.char
        
        return Pixel(char=char, color=blended_color)
    
    def render(self) -> List[List[Optional[Pixel]]]:
        """Render all layers to final output"""
        # Create output buffer
        output = [[None for _ in range(self.viewport.width)] 
                 for _ in range(self.viewport.height)]
        
        # Fill with background
        bg_pixel = Pixel(char=' ', color=self.background_color)
        for y in range(self.viewport.height):
            for x in range(self.viewport.width):
                output[y][x] = bg_pixel
        
        # Render each layer
        for layer in self.layers:
            if not layer.visible:
                continue
            
            # Apply effects
            for effect_name in layer.effects:
                effect = self.effects.get(effect_name)
                if effect:
                    effect.apply(layer)
            
            # Composite layer
            for y in range(layer.height):
                for x in range(layer.width):
                    # Calculate screen position
                    screen_x = x + layer.offset_x - self.viewport.x
                    screen_y = y + layer.offset_y - self.viewport.y
                    
                    # Check if in viewport
                    if (0 <= screen_x < self.viewport.width and
                        0 <= screen_y < self.viewport.height):
                        
                        src_pixel = layer.get_pixel(x, y)
                        if src_pixel:
                            dst_pixel = output[screen_y][screen_x]
                            output[screen_y][screen_x] = self._blend_pixels(
                                dst_pixel, src_pixel, layer.opacity, layer.blend_mode
                            )
        
        return output
    
    def render_to_string(self) -> str:
        """Render to ANSI string"""
        output = self.render()
        lines = []
        
        for row in output:
            line = ""
            current_color = None
            
            for pixel in row:
                if pixel:
                    # Apply color if changed
                    if current_color != pixel.color:
                        line += "\033[0m"  # Reset
                        line += pixel.color.to_ansi()
                        current_color = pixel.color
                    
                    line += pixel.char
                else:
                    line += " "
            
            lines.append(line + "\033[0m")  # Reset at end of line
        
        return "\n".join(lines)
    
    def set_viewport(self, x: int, y: int, width: Optional[int] = None, 
                    height: Optional[int] = None) -> None:
        """Set viewport position and size"""
        self.viewport.x = x
        self.viewport.y = y
        if width:
            self.viewport.width = width
        if height:
            self.viewport.height = height
    
    def scroll_viewport(self, dx: int, dy: int) -> None:
        """Scroll viewport"""
        self.viewport.x += dx
        self.viewport.y += dy