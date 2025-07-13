"""Particle system manager"""

from typing import List, Optional, Dict, Any, Set, Tuple
from pydantic import BaseModel, Field
import time

from .models import Particle, ParticleEmitter, ParticleEffect, Vector2D
from ..sprites.models import Pixel, Color
from ..rendering.renderer import RenderLayer, BlendMode


class ParticlePool:
    """Object pool for particles to reduce allocations"""
    
    def __init__(self, size: int = 1000):
        self.pool: List[Particle] = []
        self.active: Set[Particle] = set()
        self.size = size
    
    def acquire(self) -> Optional[Particle]:
        """Get particle from pool"""
        if self.pool:
            particle = self.pool.pop()
            self.active.add(particle)
            return particle
        elif len(self.active) < self.size:
            particle = Particle(position=Vector2D())
            self.active.add(particle)
            return particle
        return None
    
    def release(self, particle: Particle) -> None:
        """Return particle to pool"""
        if particle in self.active:
            self.active.remove(particle)
            self.pool.append(particle)


class ParticleSystem(BaseModel):
    """Main particle system manager"""
    
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    particles: List[Particle] = Field(default_factory=list)
    emitters: Dict[str, ParticleEmitter] = Field(default_factory=dict)
    effects: Dict[str, ParticleEffect] = Field(default_factory=dict)
    max_particles: int = Field(gt=0, default=1000)
    blend_mode: BlendMode = BlendMode.ADD
    
    # Performance settings
    use_physics: bool = True
    use_collision: bool = False
    collision_bounds: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    
    # Internal state
    last_update: float = Field(default_factory=time.time)
    effect_start_times: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_emitter(self, emitter: ParticleEmitter) -> None:
        """Add particle emitter"""
        self.emitters[emitter.name] = emitter
    
    def remove_emitter(self, name: str) -> None:
        """Remove emitter by name"""
        if name in self.emitters:
            del self.emitters[name]
    
    def add_effect(self, effect: ParticleEffect, position: Optional[Vector2D] = None) -> None:
        """Add particle effect"""
        self.effects[effect.name] = effect
        self.effect_start_times[effect.name] = time.time()
        
        # Update emitter positions if provided
        if position:
            for emitter in effect.emitters:
                emitter.position = position
        
        # Add emitters from effect
        for emitter in effect.emitters:
            self.add_emitter(emitter)
    
    def remove_effect(self, name: str) -> None:
        """Remove effect and its emitters"""
        if name in self.effects:
            effect = self.effects[name]
            for emitter in effect.emitters:
                self.remove_emitter(emitter.name)
            del self.effects[name]
            if name in self.effect_start_times:
                del self.effect_start_times[name]
    
    def spawn_burst(self, position: Vector2D, count: int = 10, 
                   char: str = '*', color: Optional[Color] = None) -> None:
        """Spawn burst of particles at position"""
        temp_emitter = ParticleEmitter(
            name=f"burst_{time.time()}",
            position=position,
            burst_count=count,
            particle_chars=[char],
            start_color=color or Color(r=255, g=255, b=255)
        )
        
        # Spawn particles
        new_particles = temp_emitter.update(0.0)
        for particle in new_particles:
            if len(self.particles) < self.max_particles:
                self.particles.append(particle)
    
    def update(self, dt: Optional[float] = None) -> None:
        """Update particle system"""
        current_time = time.time()
        if dt is None:
            dt = current_time - self.last_update
        self.last_update = current_time
        
        # Update existing particles
        alive_particles = []
        for particle in self.particles:
            if self.use_physics:
                particle.update(dt)
            
            # Handle collision
            if self.use_collision and self.collision_bounds:
                x, y, w, h = self.collision_bounds
                
                # Bounce off walls
                if particle.position.x < x or particle.position.x >= x + w:
                    particle.velocity.x *= -0.8  # Energy loss
                    particle.position.x = max(x, min(x + w - 1, particle.position.x))
                
                if particle.position.y < y or particle.position.y >= y + h:
                    particle.velocity.y *= -0.8
                    particle.position.y = max(y, min(y + h - 1, particle.position.y))
            
            # Color interpolation based on life
            if particle.is_alive():
                # Interpolate color (simple linear interpolation)
                t = 1.0 - particle.life
                if hasattr(particle, '_start_color'):
                    start = particle._start_color
                    end = particle._end_color
                    particle.color = Color(
                        r=int(start.r * (1 - t) + end.r * t),
                        g=int(start.g * (1 - t) + end.g * t),
                        b=int(start.b * (1 - t) + end.b * t),
                        a=start.a * (1 - t) + end.a * t
                    )
                
                alive_particles.append(particle)
        
        self.particles = alive_particles
        
        # Check effect durations
        effects_to_remove = []
        for name, effect in self.effects.items():
            if effect.duration is not None:
                elapsed = current_time - self.effect_start_times[name]
                if elapsed >= effect.duration:
                    effects_to_remove.append(name)
        
        for name in effects_to_remove:
            self.remove_effect(name)
        
        # Update emitters
        for emitter in self.emitters.values():
            new_particles = emitter.update(dt)
            
            for particle in new_particles:
                if len(self.particles) < self.max_particles:
                    # Store start/end colors for interpolation
                    particle._start_color = emitter.start_color
                    particle._end_color = emitter.end_color
                    self.particles.append(particle)
    
    def render_to_layer(self) -> RenderLayer:
        """Render particles to a render layer"""
        layer = RenderLayer(
            name="particles",
            width=self.width,
            height=self.height,
            blend_mode=self.blend_mode,
            z_order=100  # Usually on top
        )
        
        for particle in self.particles:
            x = int(particle.position.x)
            y = int(particle.position.y)
            
            if 0 <= x < self.width and 0 <= y < self.height:
                # Get character based on velocity
                char = particle.get_char_for_angle()
                
                # Apply alpha based on life
                color = Color(
                    r=particle.color.r,
                    g=particle.color.g,
                    b=particle.color.b,
                    a=particle.color.a * particle.life
                )
                
                pixel = Pixel(char=char, color=color)
                layer.set_pixel(x, y, pixel)
        
        return layer
    
    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """Get current particle count"""
        return len(self.particles)
    
    def set_collision_bounds(self, x: int, y: int, width: int, height: int) -> None:
        """Set collision boundaries"""
        self.collision_bounds = (x, y, width, height)
        self.use_collision = True
    
    def create_explosion(self, position: Vector2D) -> None:
        """Create explosion effect at position"""
        effect = ParticleEffect.create_explosion(position)
        self.add_effect(effect)
    
    def create_fire(self, position: Vector2D) -> None:
        """Create fire effect at position"""
        effect = ParticleEffect.create_fire(position)
        self.add_effect(effect)
    
    def create_sparkle(self, position: Vector2D) -> None:
        """Create sparkle effect at position"""
        effect = ParticleEffect.create_sparkle(position)
        self.add_effect(effect)