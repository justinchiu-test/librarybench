"""Tests for lighting system"""

import pytest
import math
from pytermgame.lighting import (
    LightSource, LightType, LightMap, TimeOfDay,
    LightingProcessor, OccluderMap
)
from pytermgame.sprites import Color, Pixel
from pytermgame.particles import Vector2D
from pytermgame.rendering import RenderLayer


class TestLightSource:
    """Test LightSource functionality"""
    
    def test_light_creation(self):
        """Test light source creation"""
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=50.0, y=50.0),
            color=Color(r=255, g=200, b=100),
            intensity=1.0,
            radius=20.0
        )
        
        assert light.name == "test"
        assert light.type == LightType.POINT
        assert light.position.x == 50.0
        assert light.intensity == 1.0
        assert light.enabled is True
    
    def test_point_light_intensity(self):
        """Test point light intensity calculation"""
        light = LightSource(
            name="point",
            type=LightType.POINT,
            position=Vector2D(x=0.0, y=0.0),
            intensity=1.0,
            radius=10.0,
            falloff=1.0  # Linear falloff
        )
        
        # At center
        intensity = light.get_intensity_at(Vector2D(x=0.0, y=0.0))
        assert intensity == 1.0
        
        # Halfway
        intensity = light.get_intensity_at(Vector2D(x=5.0, y=0.0))
        assert abs(intensity - 0.5) < 0.01
        
        # At edge
        intensity = light.get_intensity_at(Vector2D(x=10.0, y=0.0))
        assert intensity == 0.0
        
        # Outside radius
        intensity = light.get_intensity_at(Vector2D(x=15.0, y=0.0))
        assert intensity == 0.0
    
    def test_quadratic_falloff(self):
        """Test quadratic light falloff"""
        light = LightSource(
            name="point",
            type=LightType.POINT,
            position=Vector2D(x=0.0, y=0.0),
            intensity=1.0,
            radius=10.0,
            falloff=2.0  # Quadratic
        )
        
        # Halfway
        intensity = light.get_intensity_at(Vector2D(x=5.0, y=0.0))
        assert abs(intensity - 0.75) < 0.01  # 1 - (0.5)^2
    
    def test_directional_light(self):
        """Test directional light (constant intensity)"""
        light = LightSource(
            name="sun",
            type=LightType.DIRECTIONAL,
            position=Vector2D(x=0.0, y=0.0),
            direction=Vector2D(x=0.0, y=1.0),
            intensity=0.8
        )
        
        # Should be constant everywhere
        intensity1 = light.get_intensity_at(Vector2D(x=0.0, y=0.0))
        intensity2 = light.get_intensity_at(Vector2D(x=100.0, y=100.0))
        
        assert intensity1 == 0.8
        assert intensity2 == 0.8
    
    def test_spot_light(self):
        """Test spot light with cone"""
        light = LightSource(
            name="spot",
            type=LightType.SPOT,
            position=Vector2D(x=0.0, y=0.0),
            direction=Vector2D(x=1.0, y=0.0),  # Pointing right
            intensity=1.0,
            radius=20.0,
            cone_angle=60.0,  # 60 degree cone
            cone_softness=0.0  # Hard edge
        )
        
        # In center of cone
        intensity = light.get_intensity_at(Vector2D(x=10.0, y=0.0))
        assert intensity > 0.0
        
        # Outside cone angle
        intensity = light.get_intensity_at(Vector2D(x=0.0, y=10.0))
        assert intensity == 0.0
    
    def test_ambient_light(self):
        """Test ambient light (constant everywhere)"""
        light = LightSource(
            name="ambient",
            type=LightType.AMBIENT,
            position=Vector2D(),
            intensity=0.3
        )
        
        # Should be same everywhere
        intensity1 = light.get_intensity_at(Vector2D(x=0.0, y=0.0))
        intensity2 = light.get_intensity_at(Vector2D(x=999.0, y=999.0))
        
        assert intensity1 == 0.3
        assert intensity2 == 0.3
    
    def test_disabled_light(self):
        """Test disabled light returns zero intensity"""
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(),
            enabled=False
        )
        
        intensity = light.get_intensity_at(Vector2D(x=0.0, y=0.0))
        assert intensity == 0.0
    
    def test_light_color_at_point(self):
        """Test getting colored light at point"""
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=0.0, y=0.0),
            color=Color(r=255, g=128, b=64),
            intensity=1.0,
            radius=10.0,
            falloff=1.0
        )
        
        # At center - full color
        color = light.get_color_at(Vector2D(x=0.0, y=0.0))
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64
        
        # Halfway - half intensity
        color = light.get_color_at(Vector2D(x=5.0, y=0.0))
        assert color.r == 127
        assert color.g == 64
        assert color.b == 32


class TestLightMap:
    """Test LightMap functionality"""
    
    def test_lightmap_creation(self):
        """Test light map initialization"""
        lightmap = LightMap(width=100, height=100, scale=2)
        
        assert lightmap.width == 100
        assert lightmap.height == 100
        assert lightmap.scale == 2
        assert len(lightmap.data) == 50  # height/scale
        assert len(lightmap.data[0]) == 50  # width/scale
    
    def test_lightmap_operations(self):
        """Test get/set operations"""
        lightmap = LightMap(width=100, height=100, scale=1)
        
        # Set light
        color = Color(r=255, g=128, b=64)
        lightmap.set_light_at(50, 50, color)
        
        # Get light
        retrieved = lightmap.get_light_at(50, 50)
        assert retrieved.r == 255
        assert retrieved.g == 128
        assert retrieved.b == 64
        
        # Set shadow
        lightmap.set_shadow_at(50, 50, 0.5)
        shadow = lightmap.get_shadow_at(50, 50)
        assert shadow == 0.5
    
    def test_lightmap_scaling(self):
        """Test light map resolution scaling"""
        lightmap = LightMap(width=100, height=100, scale=4)
        
        # Set at scaled position
        lightmap.set_light_at(10, 10, Color(r=255, g=0, b=0))
        
        # Should affect 4x4 area when retrieved
        for y in range(8, 12):
            for x in range(8, 12):
                color = lightmap.get_light_at(x, y)
                assert color.r == 255
    
    def test_lightmap_clear(self):
        """Test clearing light map"""
        lightmap = LightMap(width=10, height=10, scale=1)
        
        # Fill with light
        for y in range(10):
            for x in range(10):
                lightmap.set_light_at(x, y, Color(r=255, g=255, b=255))
        
        # Clear
        lightmap.clear()
        
        # Check all black
        for y in range(10):
            for x in range(10):
                color = lightmap.get_light_at(x, y)
                assert color.r == 0
                assert color.g == 0
                assert color.b == 0


class TestTimeOfDay:
    """Test time of day system"""
    
    def test_time_creation(self):
        """Test time of day initialization"""
        tod = TimeOfDay(hour=12.0)
        
        assert tod.hour == 12.0
        assert tod.sunrise_hour == 6.0
        assert tod.sunset_hour == 18.0
    
    def test_sun_angle(self):
        """Test sun angle calculation"""
        tod = TimeOfDay()
        
        # Midnight - below horizon
        tod.hour = 0.0
        assert tod.get_sun_angle() == -30.0
        
        # Noon - zenith
        tod.hour = 12.0
        assert tod.get_sun_angle() == 90.0
        
        # Sunrise
        tod.hour = 6.0
        assert tod.get_sun_angle() == 0.0
        
        # Sunset
        tod.hour = 18.0
        assert abs(tod.get_sun_angle()) < 0.1
    
    def test_ambient_light_cycle(self):
        """Test ambient light throughout day"""
        tod = TimeOfDay()
        
        # Night
        tod.hour = 0.0
        color, intensity = tod.get_ambient_light()
        assert intensity == tod.night_ambient
        
        # Dawn
        tod.hour = 6.0
        color, intensity = tod.get_ambient_light()
        assert intensity == tod.dawn_ambient
        
        # Noon
        tod.hour = 12.0
        color, intensity = tod.get_ambient_light()
        assert intensity == tod.noon_ambient
        
        # Dusk
        tod.hour = 18.0
        color, intensity = tod.get_ambient_light()
        assert intensity == tod.dusk_ambient
    
    def test_color_interpolation(self):
        """Test color interpolation between times"""
        tod = TimeOfDay()
        
        # Between night and dawn (3 AM)
        tod.hour = 3.0
        color, _ = tod.get_ambient_light()
        
        # Should be between night and dawn colors
        assert tod.night_color.r <= color.r <= tod.dawn_color.r
        assert tod.night_color.g <= color.g <= tod.dawn_color.g
        assert tod.night_color.b <= color.b <= tod.dawn_color.b
    
    def test_time_advancement(self):
        """Test time progression"""
        tod = TimeOfDay(hour=23.0)
        
        # Advance 2 hours
        tod.advance_time(2.0)
        assert tod.hour == 1.0  # Wrapped around
        
        # Advance fractional hours
        tod.advance_time(0.5)
        assert tod.hour == 1.5


class TestOccluderMap:
    """Test occluder map for shadows"""
    
    def test_occluder_creation(self):
        """Test occluder map initialization"""
        occluders = OccluderMap(width=50, height=50)
        
        assert occluders.width == 50
        assert occluders.height == 50
        
        # Should start empty
        for y in range(50):
            for x in range(50):
                assert occluders.is_occluder(x, y) is False
    
    def test_occluder_operations(self):
        """Test setting/checking occluders"""
        occluders = OccluderMap(width=10, height=10)
        
        # Set occluder
        occluders.set_occluder(5, 5, True)
        assert occluders.is_occluder(5, 5) is True
        
        # Clear occluder
        occluders.set_occluder(5, 5, False)
        assert occluders.is_occluder(5, 5) is False
        
        # Out of bounds
        assert occluders.is_occluder(20, 20) is False
    
    def test_occluder_from_layer(self):
        """Test building occluder map from render layer"""
        layer = RenderLayer(name="test", width=10, height=10)
        
        # Add some opaque pixels
        layer.set_pixel(3, 3, Pixel(char='#', color=Color(r=255, g=255, b=255, a=1.0)))
        layer.set_pixel(5, 5, Pixel(char='#', color=Color(r=255, g=255, b=255, a=0.3)))
        
        occluders = OccluderMap(width=10, height=10)
        occluders.from_layer(layer, threshold=0.5)
        
        # High alpha should occlude
        assert occluders.is_occluder(3, 3) is True
        
        # Low alpha should not
        assert occluders.is_occluder(5, 5) is False


class TestLightingProcessor:
    """Test main lighting processor"""
    
    def test_processor_creation(self):
        """Test processor initialization"""
        processor = LightingProcessor(width=100, height=100)
        
        assert processor.width == 100
        assert processor.height == 100
        assert len(processor.lights) == 0
        assert processor.occluders is not None
        assert processor.light_map is not None
        assert processor.time_of_day is not None
    
    def test_light_management(self):
        """Test adding/removing lights"""
        processor = LightingProcessor(width=100, height=100)
        
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=50.0, y=50.0)
        )
        
        processor.add_light(light)
        assert "test" in processor.lights
        
        processor.remove_light("test")
        assert "test" not in processor.lights
    
    def test_basic_lighting_calculation(self):
        """Test basic lighting without shadows"""
        processor = LightingProcessor(width=20, height=20)
        processor.shadow_rays = 4  # Reduce for faster test
        
        # Add point light
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=10.0, y=10.0),
            intensity=1.0,
            radius=10.0,
            cast_shadows=False
        )
        processor.add_light(light)
        
        # Calculate
        processor.calculate_lighting()
        
        # Check center is bright
        center_light = processor.get_light_at_position(10, 10)
        assert center_light.r > 200
        
        # Check falloff
        edge_light = processor.get_light_at_position(15, 10)
        assert edge_light.r < center_light.r
    
    def test_shadow_calculation(self):
        """Test shadow casting"""
        processor = LightingProcessor(width=30, height=30)
        processor.shadow_rays = 4
        
        # Add light
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=10.0, y=10.0),
            intensity=1.0,
            radius=20.0,
            cast_shadows=True
        )
        processor.add_light(light)
        
        # Add occluder between light and test point
        processor.occluders.set_occluder(15, 10, True)
        
        # Calculate
        processor.calculate_lighting()
        
        # Point behind occluder should be in shadow
        shadow = processor.get_shadow_at_position(20, 10)
        assert shadow > 0.0
    
    def test_ambient_occlusion(self):
        """Test ambient occlusion calculation"""
        processor = LightingProcessor(width=20, height=20)
        processor.ambient_occlusion = True
        processor.ao_radius = 3
        processor.ao_samples = 4
        
        # Create enclosed area
        for x in range(5, 15):
            processor.occluders.set_occluder(x, 5, True)
            processor.occluders.set_occluder(x, 15, True)
        for y in range(5, 15):
            processor.occluders.set_occluder(5, y, True)
            processor.occluders.set_occluder(15, y, True)
        
        # Calculate
        processor.calculate_lighting()
        
        # Corners should have more occlusion
        corner_light = processor.get_light_at_position(6, 6)
        center_light = processor.get_light_at_position(10, 10)
        
        # Corner should be darker due to AO
        assert corner_light.r < center_light.r
    
    def test_apply_lighting_to_layer(self):
        """Test applying lighting to render layer"""
        processor = LightingProcessor(width=20, height=20)
        
        # Add light
        light = LightSource(
            name="test",
            type=LightType.POINT,
            position=Vector2D(x=10.0, y=10.0),
            color=Color(r=255, g=255, b=255),
            intensity=1.0,
            radius=15.0
        )
        processor.add_light(light)
        processor.calculate_lighting()
        
        # Create layer with white pixels
        layer = RenderLayer(name="test", width=20, height=20)
        layer.set_pixel(10, 10, Pixel(char='#', color=Color(r=255, g=255, b=255)))
        layer.set_pixel(15, 10, Pixel(char='#', color=Color(r=255, g=255, b=255)))
        
        # Apply lighting
        lit_layer = processor.apply_lighting_to_layer(layer)
        
        # Center pixel should be bright
        center = lit_layer.get_pixel(10, 10)
        assert center is not None
        assert center.color.r > 200
        
        # Edge pixel should be dimmer
        edge = lit_layer.get_pixel(15, 10)
        assert edge is not None
        assert edge.color.r < center.color.r
    
    def test_torch_light_creation(self):
        """Test convenience torch light creation"""
        processor = LightingProcessor(width=50, height=50)
        
        torch = processor.create_torch_light(Vector2D(x=25.0, y=25.0), "torch1")
        
        assert torch.name == "torch1"
        assert torch.type == LightType.POINT
        assert torch.color.r == 255
        assert torch.color.g == 200
        assert torch.cast_shadows is True
        assert "torch1" in processor.lights
    
    def test_sun_light_creation(self):
        """Test sun light based on time of day"""
        processor = LightingProcessor(width=50, height=50)
        processor.set_time_of_day(12.0)  # Noon
        
        sun = processor.create_sun_light()
        
        assert sun.name == "sun"
        assert sun.type == LightType.DIRECTIONAL
        assert sun.intensity > 0.0
        assert "sun" in processor.lights
    
    def test_time_of_day_integration(self):
        """Test time of day affects ambient lighting"""
        processor = LightingProcessor(width=20, height=20)
        
        # Night time
        processor.set_time_of_day(0.0)
        processor.calculate_lighting()
        night_light = processor.get_light_at_position(10, 10)
        
        # Noon time
        processor.set_time_of_day(12.0)
        processor.calculate_lighting()
        noon_light = processor.get_light_at_position(10, 10)
        
        # Noon should be brighter
        assert noon_light.r > night_light.r
        assert noon_light.g > night_light.g
        assert noon_light.b > night_light.b