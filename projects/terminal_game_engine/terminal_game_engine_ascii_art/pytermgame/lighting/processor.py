"""Lighting processor for calculating illumination and shadows"""

from typing import List, Optional, Dict, Tuple, Set
from pydantic import BaseModel, Field
import math

from .models import LightSource, LightMap, Shadow, TimeOfDay, LightType
from ..sprites.models import Color, Pixel
from ..particles.models import Vector2D
from ..rendering.renderer import RenderLayer


class OccluderMap(BaseModel):
    """Map of objects that block light"""
    
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    data: List[List[bool]] = Field(default_factory=list)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.data:
            self.data = [[False for _ in range(self.width)] for _ in range(self.height)]
    
    def set_occluder(self, x: int, y: int, blocks: bool = True) -> None:
        """Set whether position blocks light"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = blocks
    
    def is_occluder(self, x: int, y: int) -> bool:
        """Check if position blocks light"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return False
    
    def clear(self) -> None:
        """Clear all occluders"""
        for y in range(self.height):
            for x in range(self.width):
                self.data[y][x] = False
    
    def from_layer(self, layer: RenderLayer, threshold: float = 0.5) -> None:
        """Build occluder map from render layer"""
        self.width = layer.width
        self.height = layer.height
        self.data = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                pixel = layer.get_pixel(x, y)
                if pixel and pixel.color.a > threshold:
                    self.data[y][x] = True


class LightingProcessor:
    """Process lighting calculations"""
    
    def __init__(self, width: int, height: int):
        """Initialize processor"""
        self.width = width
        self.height = height
        self.lights: Dict[str, LightSource] = {}
        self.occluders = OccluderMap(width=width, height=height)
        self.light_map = LightMap(width=width, height=height, scale=2)
        self.time_of_day = TimeOfDay()
        
        # Performance settings
        self.shadow_rays: int = 8  # Number of rays for soft shadows
        self.max_shadow_distance: float = 50.0
        self.ambient_occlusion: bool = True
        self.ao_radius: int = 3
        self.ao_samples: int = 8
    
    def add_light(self, light: LightSource) -> None:
        """Add light source"""
        self.lights[light.name] = light
    
    def remove_light(self, name: str) -> None:
        """Remove light source"""
        if name in self.lights:
            del self.lights[name]
    
    def update_occluders(self, layer: RenderLayer) -> None:
        """Update occluder map from render layer"""
        self.occluders.from_layer(layer)
    
    def _cast_ray(self, start: Vector2D, end: Vector2D) -> bool:
        """Cast ray and check for occlusion"""
        # Bresenham's line algorithm
        x0, y0 = int(start.x), int(start.y)
        x1, y1 = int(end.x), int(end.y)
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        
        x_inc = 1 if x0 < x1 else -1
        y_inc = 1 if y0 < y1 else -1
        
        if dx > dy:
            error = dx / 2.0
            while x != x1:
                if self.occluders.is_occluder(x, y):
                    return True
                error -= dy
                if error < 0:
                    y += y_inc
                    error += dx
                x += x_inc
        else:
            error = dy / 2.0
            while y != y1:
                if self.occluders.is_occluder(x, y):
                    return True
                error -= dx
                if error < 0:
                    x += x_inc
                    error += dy
                y += y_inc
        
        return False
    
    def _calculate_shadow(self, point: Vector2D, light: LightSource) -> float:
        """Calculate shadow occlusion for a point"""
        if not light.cast_shadows:
            return 0.0
        
        occlusion = 0.0
        
        if light.type == LightType.POINT or light.type == LightType.SPOT:
            # Cast multiple rays for soft shadows
            for i in range(self.shadow_rays):
                angle = (i / self.shadow_rays) * 2 * math.pi
                
                # Add small offset for soft shadows
                offset_x = math.cos(angle) * light.shadow_softness
                offset_y = math.sin(angle) * light.shadow_softness
                
                light_pos = Vector2D(
                    x=light.position.x + offset_x,
                    y=light.position.y + offset_y
                )
                
                if self._cast_ray(point, light_pos):
                    occlusion += 1.0 / self.shadow_rays
        
        elif light.type == LightType.DIRECTIONAL:
            # Cast ray in opposite direction of light
            ray_end = Vector2D(
                x=point.x - light.direction.x * self.max_shadow_distance,
                y=point.y - light.direction.y * self.max_shadow_distance
            )
            
            if self._cast_ray(point, ray_end):
                occlusion = 1.0
        
        return min(1.0, occlusion)
    
    def _calculate_ambient_occlusion(self, x: int, y: int) -> float:
        """Calculate ambient occlusion at position"""
        if not self.ambient_occlusion:
            return 0.0
        
        occlusion = 0.0
        samples = 0
        
        # Sample surrounding area
        for i in range(self.ao_samples):
            angle = (i / self.ao_samples) * 2 * math.pi
            
            for r in range(1, self.ao_radius + 1):
                sample_x = x + int(math.cos(angle) * r)
                sample_y = y + int(math.sin(angle) * r)
                
                if self.occluders.is_occluder(sample_x, sample_y):
                    # Closer occluders have more impact
                    occlusion += (self.ao_radius - r + 1) / self.ao_radius
                
                samples += 1
        
        return min(1.0, occlusion / samples) if samples > 0 else 0.0
    
    def calculate_lighting(self) -> None:
        """Calculate full lighting for scene"""
        self.light_map.clear()
        
        # Get ambient light from time of day
        ambient_color, ambient_intensity = self.time_of_day.get_ambient_light()
        
        # Process each point in light map
        for ly in range(self.light_map.height // self.light_map.scale):
            for lx in range(self.light_map.width // self.light_map.scale):
                # Convert to world coordinates
                x = lx * self.light_map.scale
                y = ly * self.light_map.scale
                point = Vector2D(x=x, y=y)
                
                # Start with ambient light
                total_r = ambient_color.r * ambient_intensity
                total_g = ambient_color.g * ambient_intensity
                total_b = ambient_color.b * ambient_intensity
                
                # Calculate ambient occlusion
                ao = self._calculate_ambient_occlusion(x, y)
                ao_factor = 1.0 - ao * 0.5  # Reduce by up to 50%
                
                total_r *= ao_factor
                total_g *= ao_factor
                total_b *= ao_factor
                
                # Add contribution from each light
                total_shadow = 0.0
                
                for light in self.lights.values():
                    if not light.enabled:
                        continue
                    
                    # Get light contribution
                    light_color = light.get_color_at(point)
                    
                    # Calculate shadows
                    shadow = self._calculate_shadow(point, light)
                    shadow_factor = 1.0 - shadow
                    
                    # Add light contribution
                    total_r += light_color.r * shadow_factor
                    total_g += light_color.g * shadow_factor
                    total_b += light_color.b * shadow_factor
                    
                    total_shadow = max(total_shadow, shadow)
                
                # Clamp and set final color
                final_color = Color(
                    r=min(255, int(total_r)),
                    g=min(255, int(total_g)),
                    b=min(255, int(total_b))
                )
                
                self.light_map.set_light_at(x, y, final_color)
                self.light_map.set_shadow_at(x, y, total_shadow)
    
    def apply_lighting_to_layer(self, layer: RenderLayer) -> RenderLayer:
        """Apply lighting to a render layer"""
        lit_layer = RenderLayer(
            name=f"{layer.name}_lit",
            width=layer.width,
            height=layer.height,
            z_order=layer.z_order
        )
        
        for y in range(layer.height):
            for x in range(layer.width):
                pixel = layer.get_pixel(x, y)
                if pixel:
                    # Get lighting at this position
                    light_color = self.light_map.get_light_at(x, y)
                    
                    # Apply lighting to pixel color
                    lit_r = (pixel.color.r * light_color.r) // 255
                    lit_g = (pixel.color.g * light_color.g) // 255
                    lit_b = (pixel.color.b * light_color.b) // 255
                    
                    lit_pixel = Pixel(
                        char=pixel.char,
                        color=Color(r=lit_r, g=lit_g, b=lit_b, a=pixel.color.a)
                    )
                    
                    lit_layer.set_pixel(x, y, lit_pixel)
        
        return lit_layer
    
    def get_light_at_position(self, x: int, y: int) -> Color:
        """Get calculated light color at position"""
        return self.light_map.get_light_at(x, y)
    
    def get_shadow_at_position(self, x: int, y: int) -> float:
        """Get shadow occlusion at position"""
        return self.light_map.get_shadow_at(x, y)
    
    def set_time_of_day(self, hour: float) -> None:
        """Set time of day"""
        self.time_of_day.hour = hour % 24.0
    
    def advance_time(self, hours: float) -> None:
        """Advance time by hours"""
        self.time_of_day.advance_time(hours)
    
    def create_torch_light(self, position: Vector2D, name: Optional[str] = None) -> LightSource:
        """Create flickering torch light"""
        import random
        
        base_intensity = 0.8 + random.random() * 0.4
        
        light = LightSource(
            name=name or f"torch_{id(position)}",
            type=LightType.POINT,
            position=position,
            color=Color(r=255, g=200, b=100),
            intensity=base_intensity,
            radius=8.0,
            falloff=1.5,
            cast_shadows=True,
            shadow_softness=0.3
        )
        
        self.add_light(light)
        return light
    
    def create_sun_light(self) -> LightSource:
        """Create directional sun light based on time of day"""
        sun_angle = self.time_of_day.get_sun_angle()
        ambient_color, _ = self.time_of_day.get_ambient_light()
        
        # Calculate sun direction from angle
        angle_rad = math.radians(sun_angle)
        direction = Vector2D(
            x=math.cos(angle_rad),
            y=math.sin(angle_rad)
        )
        
        light = LightSource(
            name="sun",
            type=LightType.DIRECTIONAL,
            position=Vector2D(x=0, y=0),  # Position doesn't matter for directional
            direction=direction,
            color=ambient_color,
            intensity=max(0.0, math.sin(angle_rad)),  # Intensity based on angle
            cast_shadows=True
        )
        
        self.add_light(light)
        return light