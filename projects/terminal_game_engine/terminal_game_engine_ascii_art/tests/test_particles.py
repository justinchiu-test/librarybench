"""Tests for particle system"""

import pytest
import time
import math
from pytermgame.particles import (
    Vector2D, Particle, ParticleEmitter, ParticleEffect,
    ParticleSystem
)
from pytermgame.sprites import Color
from pytermgame.rendering import BlendMode


class TestVector2D:
    """Test Vector2D operations"""
    
    def test_vector_creation(self):
        """Test vector creation"""
        vec = Vector2D(x=3.0, y=4.0)
        assert vec.x == 3.0
        assert vec.y == 4.0
    
    def test_vector_operations(self):
        """Test vector math operations"""
        v1 = Vector2D(x=3.0, y=4.0)
        v2 = Vector2D(x=1.0, y=2.0)
        
        # Addition
        v3 = v1.add(v2)
        assert v3.x == 4.0
        assert v3.y == 6.0
        
        # Subtraction
        v4 = v1.subtract(v2)
        assert v4.x == 2.0
        assert v4.y == 2.0
        
        # Scalar multiplication
        v5 = v1.multiply(2.0)
        assert v5.x == 6.0
        assert v5.y == 8.0
    
    def test_vector_magnitude(self):
        """Test magnitude calculation"""
        vec = Vector2D(x=3.0, y=4.0)
        assert vec.magnitude() == 5.0  # 3-4-5 triangle
    
    def test_vector_normalize(self):
        """Test vector normalization"""
        vec = Vector2D(x=3.0, y=4.0)
        norm = vec.normalize()
        
        assert abs(norm.magnitude() - 1.0) < 0.001
        assert abs(norm.x - 0.6) < 0.001
        assert abs(norm.y - 0.8) < 0.001
    
    def test_vector_dot_product(self):
        """Test dot product"""
        v1 = Vector2D(x=3.0, y=4.0)
        v2 = Vector2D(x=2.0, y=1.0)
        
        dot = v1.dot(v2)
        assert dot == 10.0  # 3*2 + 4*1


class TestParticle:
    """Test Particle functionality"""
    
    def test_particle_creation(self):
        """Test particle creation"""
        pos = Vector2D(x=10.0, y=20.0)
        vel = Vector2D(x=5.0, y=-5.0)
        
        particle = Particle(
            position=pos,
            velocity=vel,
            char='*',
            lifetime=2.0
        )
        
        assert particle.position.x == 10.0
        assert particle.position.y == 20.0
        assert particle.char == '*'
        assert particle.life == 1.0
        assert particle.lifetime == 2.0
    
    def test_particle_update(self):
        """Test particle physics update"""
        particle = Particle(
            position=Vector2D(x=0.0, y=0.0),
            velocity=Vector2D(x=10.0, y=0.0),
            acceleration=Vector2D(x=0.0, y=10.0),  # Gravity
            lifetime=1.0
        )
        
        # Update for 0.1 seconds
        particle.update(0.1)
        
        # Position should change based on velocity
        assert particle.position.x == 1.0  # 10 * 0.1
        assert particle.position.y == 0.0  # No initial y velocity
        
        # Velocity should change based on acceleration
        assert particle.velocity.x == 10.0  # No x acceleration
        assert particle.velocity.y == 1.0   # 10 * 0.1
    
    def test_particle_lifetime(self):
        """Test particle life tracking"""
        particle = Particle(
            position=Vector2D(),
            lifetime=1.0
        )
        
        # Initially alive
        assert particle.is_alive() is True
        assert particle.life == 1.0
        
        # Simulate aging
        particle.created_at = time.time() - 0.5
        particle.update(0.0)
        
        assert particle.life == 0.5
        assert particle.is_alive() is True
        
        # Simulate death
        particle.created_at = time.time() - 1.5
        particle.update(0.0)
        
        assert particle.life == 0.0
        assert particle.is_alive() is False
    
    def test_particle_rotation(self):
        """Test particle rotation"""
        particle = Particle(
            position=Vector2D(),
            rotation=0.0,
            angular_velocity=math.pi  # Half rotation per second
        )
        
        particle.update(0.5)
        assert abs(particle.rotation - math.pi / 2) < 0.001
    
    def test_particle_char_for_angle(self):
        """Test directional character selection"""
        particle = Particle(position=Vector2D())
        
        # Test various directions
        particle.velocity = Vector2D(x=10.0, y=0.0)  # Right
        assert particle.get_char_for_angle() == '-'
        
        particle.velocity = Vector2D(x=0.0, y=10.0)  # Down
        assert particle.get_char_for_angle() == '|'
        
        particle.velocity = Vector2D(x=10.0, y=10.0)  # Diagonal
        assert particle.get_char_for_angle() == '\\'


class TestParticleEmitter:
    """Test ParticleEmitter functionality"""
    
    def test_emitter_creation(self):
        """Test emitter initialization"""
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(x=50.0, y=50.0),
            emission_rate=10.0
        )
        
        assert emitter.name == "test"
        assert emitter.position.x == 50.0
        assert emitter.emission_rate == 10.0
        assert emitter.enabled is True
    
    def test_spawn_positions(self):
        """Test different spawn shapes"""
        # Point emitter
        point_emitter = ParticleEmitter(
            name="point",
            position=Vector2D(x=10.0, y=10.0),
            shape="point"
        )
        pos = point_emitter.get_spawn_position()
        assert pos.x == 10.0
        assert pos.y == 10.0
        
        # Circle emitter
        circle_emitter = ParticleEmitter(
            name="circle",
            position=Vector2D(x=50.0, y=50.0),
            shape="circle",
            shape_params={"radius": 10.0}
        )
        
        # Test multiple spawns are within radius
        for _ in range(10):
            pos = circle_emitter.get_spawn_position()
            distance = pos.subtract(circle_emitter.position).magnitude()
            assert distance <= 10.0
        
        # Rectangle emitter
        rect_emitter = ParticleEmitter(
            name="rect",
            position=Vector2D(x=50.0, y=50.0),
            shape="rectangle",
            shape_params={"width": 20.0, "height": 10.0}
        )
        
        for _ in range(10):
            pos = rect_emitter.get_spawn_position()
            assert 40.0 <= pos.x <= 60.0
            assert 45.0 <= pos.y <= 55.0
    
    def test_particle_creation(self):
        """Test particle creation with emitter settings"""
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(x=0.0, y=0.0),
            particle_chars=['*', '+'],
            particle_lifetime=(1.0, 2.0),
            particle_speed=(10.0, 20.0),
            particle_direction=(0.0, 90.0),  # Right to down
            start_color=Color(r=255, g=0, b=0)
        )
        
        particle = emitter.create_particle()
        
        assert particle.char in ['*', '+']
        assert 1.0 <= particle.lifetime <= 2.0
        
        # Check velocity is in correct range
        speed = particle.velocity.magnitude()
        assert 10.0 <= speed <= 20.0
        
        # Check color
        assert particle.color.r >= 200  # Some variance allowed
    
    def test_continuous_emission(self):
        """Test continuous particle emission"""
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(),
            emission_rate=10.0  # 10 particles per second
        )
        
        # Update for 0.5 seconds
        particles = emitter.update(0.5)
        
        # Should emit ~5 particles
        assert 4 <= len(particles) <= 6
    
    def test_burst_emission(self):
        """Test burst particle emission"""
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(),
            emission_rate=0.0
        )
        
        # Trigger burst
        emitter.burst(20)
        particles = emitter.update(0.0)
        
        assert len(particles) == 20
        
        # Second update should not emit more
        particles2 = emitter.update(0.1)
        assert len(particles2) == 0
    
    def test_emitter_disabling(self):
        """Test disabling emitter"""
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(),
            emission_rate=10.0
        )
        
        emitter.enabled = False
        particles = emitter.update(1.0)
        
        assert len(particles) == 0


class TestParticleEffect:
    """Test predefined particle effects"""
    
    def test_explosion_effect(self):
        """Test explosion effect creation"""
        pos = Vector2D(x=50.0, y=50.0)
        effect = ParticleEffect.create_explosion(pos)
        
        assert effect.name == "explosion"
        assert len(effect.emitters) == 1
        assert effect.duration == 1.0
        
        emitter = effect.emitters[0]
        assert emitter.burst_count == 50
        assert emitter.emission_rate == 0
        assert '*' in emitter.particle_chars
    
    def test_fire_effect(self):
        """Test fire effect creation"""
        pos = Vector2D(x=50.0, y=50.0)
        effect = ParticleEffect.create_fire(pos)
        
        assert effect.name == "fire"
        assert effect.duration is None  # Continuous
        
        emitter = effect.emitters[0]
        assert emitter.emission_rate > 0
        assert emitter.gravity.y < 0  # Negative gravity for upward motion
        assert '^' in emitter.particle_chars
    
    def test_sparkle_effect(self):
        """Test sparkle effect creation"""
        pos = Vector2D(x=50.0, y=50.0)
        effect = ParticleEffect.create_sparkle(pos)
        
        assert effect.name == "sparkle"
        assert effect.duration is None
        
        emitter = effect.emitters[0]
        assert emitter.emission_rate > 0
        assert emitter.color_variance > 0


class TestParticleSystem:
    """Test main particle system"""
    
    def test_system_creation(self):
        """Test particle system initialization"""
        system = ParticleSystem(width=100, height=100)
        
        assert system.width == 100
        assert system.height == 100
        assert system.max_particles == 1000
        assert len(system.particles) == 0
    
    def test_emitter_management(self):
        """Test adding/removing emitters"""
        system = ParticleSystem(width=100, height=100)
        
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(x=50.0, y=50.0)
        )
        
        system.add_emitter(emitter)
        assert "test" in system.emitters
        
        system.remove_emitter("test")
        assert "test" not in system.emitters
    
    def test_effect_management(self):
        """Test adding/removing effects"""
        system = ParticleSystem(width=100, height=100)
        
        effect = ParticleEffect.create_explosion(Vector2D(x=50.0, y=50.0))
        system.add_effect(effect)
        
        assert "explosion" in system.effects
        assert len(system.emitters) > 0
        
        system.remove_effect("explosion")
        assert "explosion" not in system.effects
        assert len(system.emitters) == 0
    
    def test_spawn_burst(self):
        """Test manual burst spawning"""
        system = ParticleSystem(width=100, height=100)
        
        system.spawn_burst(
            position=Vector2D(x=50.0, y=50.0),
            count=10,
            char='*',
            color=Color(r=255, g=0, b=0)
        )
        
        assert len(system.particles) == 10
        assert all(p.char == '*' for p in system.particles)
    
    def test_particle_update(self):
        """Test particle system update"""
        system = ParticleSystem(width=100, height=100)
        
        # Add some particles
        for _ in range(5):
            particle = Particle(
                position=Vector2D(x=50.0, y=50.0),
                velocity=Vector2D(x=10.0, y=0.0),
                lifetime=1.0
            )
            system.particles.append(particle)
        
        # Update
        system.update(0.1)
        
        # Check particles moved
        for particle in system.particles:
            assert particle.position.x > 50.0
    
    def test_particle_lifetime_management(self):
        """Test removal of dead particles"""
        system = ParticleSystem(width=100, height=100)
        
        # Add particle that's already dead
        dead_particle = Particle(
            position=Vector2D(),
            lifetime=0.5
        )
        dead_particle.created_at = time.time() - 1.0
        
        system.particles.append(dead_particle)
        system.update(0.1)
        
        # Dead particle should be removed
        assert len(system.particles) == 0
    
    def test_collision_bounds(self):
        """Test particle collision with boundaries"""
        system = ParticleSystem(width=100, height=100)
        system.set_collision_bounds(0, 0, 100, 100)
        
        # Add particle moving out of bounds
        particle = Particle(
            position=Vector2D(x=95.0, y=50.0),
            velocity=Vector2D(x=20.0, y=0.0),
            lifetime=10.0
        )
        system.particles.append(particle)
        
        system.update(0.5)
        
        # Should bounce back
        assert particle.position.x < 100
        assert particle.velocity.x < 0  # Reversed direction
    
    def test_max_particles_limit(self):
        """Test particle count limiting"""
        system = ParticleSystem(width=100, height=100, max_particles=10)
        
        emitter = ParticleEmitter(
            name="test",
            position=Vector2D(),
            emission_rate=100.0  # High rate
        )
        
        system.add_emitter(emitter)
        system.update(1.0)
        
        # Should not exceed max
        assert len(system.particles) <= 10
    
    def test_render_to_layer(self):
        """Test rendering particles to layer"""
        system = ParticleSystem(width=100, height=100)
        
        # Add visible particle
        particle = Particle(
            position=Vector2D(x=50.0, y=50.0),
            char='*',
            color=Color(r=255, g=0, b=0),
            lifetime=1.0
        )
        system.particles.append(particle)
        
        # Render
        layer = system.render_to_layer()
        
        assert layer.name == "particles"
        assert layer.width == 100
        assert layer.height == 100
        assert layer.blend_mode == BlendMode.ADD
        
        # Check particle rendered
        pixel = layer.get_pixel(50, 50)
        assert pixel is not None
        assert pixel.char == '*'
        assert pixel.color.r == 255
    
    def test_effect_duration(self):
        """Test timed effect removal"""
        system = ParticleSystem(width=100, height=100)
        
        # Add effect with duration
        effect = ParticleEffect(
            name="timed",
            emitters=[],
            duration=0.5
        )
        
        system.add_effect(effect)
        assert "timed" in system.effects
        
        # Simulate time passing
        system._effect_start_times["timed"] = time.time() - 1.0
        system.update(0.1)
        
        # Effect should be removed
        assert "timed" not in system.effects
    
    def test_convenience_effects(self):
        """Test convenience effect creation methods"""
        system = ParticleSystem(width=100, height=100)
        
        pos = Vector2D(x=50.0, y=50.0)
        
        # Explosion
        system.create_explosion(pos)
        assert "explosion" in system.effects
        
        # Fire
        system.create_fire(pos)
        assert "fire" in system.effects
        
        # Sparkle
        system.create_sparkle(pos)
        assert "sparkle" in system.effects