"""Tests for sprite system"""

import pytest
from pytermgame.sprites import (
    Sprite, Layer, Pixel, Color, Palette,
    SpriteEditor, EditMode,
    PencilTool, BrushTool, LineTool, RectangleTool, CircleTool, FillTool
)


class TestColor:
    """Test Color model"""
    
    def test_color_creation(self):
        """Test color creation and validation"""
        color = Color(r=128, g=64, b=255, a=0.5)
        assert color.r == 128
        assert color.g == 64
        assert color.b == 255
        assert color.a == 0.5
    
    def test_color_to_ansi(self):
        """Test ANSI color code generation"""
        color = Color(r=255, g=128, b=0)
        ansi = color.to_ansi()
        assert ansi == "\033[38;2;255;128;0m"
    
    def test_color_blend(self):
        """Test color blending"""
        color1 = Color(r=255, g=0, b=0)
        color2 = Color(r=0, g=255, b=0)
        blended = color1.blend(color2, 0.5)
        
        assert blended.r == 127
        assert blended.g == 127
        assert blended.b == 0


class TestPixel:
    """Test Pixel model"""
    
    def test_pixel_creation(self):
        """Test pixel creation"""
        color = Color(r=255, g=255, b=255)
        pixel = Pixel(char='#', color=color)
        
        assert pixel.char == '#'
        assert pixel.color.r == 255
    
    def test_pixel_char_validation(self):
        """Test single character validation"""
        with pytest.raises(ValueError):
            Pixel(char='ab', color=Color(r=0, g=0, b=0))


class TestLayer:
    """Test Layer functionality"""
    
    def test_layer_creation(self):
        """Test layer creation and initialization"""
        layer = Layer(name="Test", width=10, height=10)
        
        assert layer.name == "Test"
        assert layer.width == 10
        assert layer.height == 10
        assert len(layer.pixels) == 10
        assert len(layer.pixels[0]) == 10
    
    def test_pixel_operations(self):
        """Test get/set pixel operations"""
        layer = Layer(name="Test", width=5, height=5)
        pixel = Pixel(char='*', color=Color(r=255, g=0, b=0))
        
        # Set pixel
        layer.set_pixel(2, 2, pixel)
        
        # Get pixel
        retrieved = layer.get_pixel(2, 2)
        assert retrieved is not None
        assert retrieved.char == '*'
        assert retrieved.color.r == 255
        
        # Out of bounds
        assert layer.get_pixel(10, 10) is None
    
    def test_layer_clear(self):
        """Test clearing layer"""
        layer = Layer(name="Test", width=3, height=3)
        pixel = Pixel(char='#', color=Color(r=255, g=255, b=255))
        
        # Fill layer
        for y in range(3):
            for x in range(3):
                layer.set_pixel(x, y, pixel)
        
        # Clear
        layer.clear()
        
        # Check all pixels are None
        for y in range(3):
            for x in range(3):
                assert layer.get_pixel(x, y) is None
    
    def test_layer_resize(self):
        """Test layer resizing"""
        layer = Layer(name="Test", width=3, height=3)
        pixel = Pixel(char='#', color=Color(r=255, g=255, b=255))
        
        # Set some pixels
        layer.set_pixel(1, 1, pixel)
        layer.set_pixel(2, 2, pixel)
        
        # Resize larger
        layer.resize(5, 5)
        assert layer.width == 5
        assert layer.height == 5
        assert layer.get_pixel(1, 1) is not None
        assert layer.get_pixel(2, 2) is not None
        assert layer.get_pixel(4, 4) is None
        
        # Resize smaller
        layer.resize(2, 2)
        assert layer.width == 2
        assert layer.height == 2
        assert layer.get_pixel(1, 1) is not None


class TestSprite:
    """Test Sprite functionality"""
    
    def test_sprite_creation(self):
        """Test sprite creation"""
        sprite = Sprite(name="Test", width=16, height=16)
        
        assert sprite.name == "Test"
        assert sprite.width == 16
        assert sprite.height == 16
        assert len(sprite.layers) == 0
    
    def test_layer_management(self):
        """Test layer add/remove/get operations"""
        sprite = Sprite(name="Test", width=10, height=10)
        
        # Add layers
        layer1 = sprite.add_layer("Layer1")
        layer2 = sprite.add_layer("Layer2")
        
        assert len(sprite.layers) == 2
        assert sprite.layers[0].name == "Layer1"
        assert sprite.layers[1].name == "Layer2"
        
        # Get layer by name
        found = sprite.get_layer("Layer1")
        assert found is not None
        assert found.name == "Layer1"
        
        # Remove layer
        sprite.remove_layer(0)
        assert len(sprite.layers) == 1
        assert sprite.layers[0].name == "Layer2"
    
    def test_layer_ordering(self):
        """Test layer z-order management"""
        sprite = Sprite(name="Test", width=10, height=10)
        
        sprite.add_layer("Layer1")
        sprite.add_layer("Layer2")
        sprite.add_layer("Layer3")
        
        # Move layer
        sprite.move_layer(0, 2)
        
        assert sprite.layers[0].name == "Layer2"
        assert sprite.layers[1].name == "Layer3"
        assert sprite.layers[2].name == "Layer1"
    
    def test_sprite_composite(self):
        """Test layer compositing"""
        sprite = Sprite(name="Test", width=3, height=3)
        
        # Add two layers
        layer1 = sprite.add_layer("Background")
        layer2 = sprite.add_layer("Foreground")
        
        # Set pixels
        bg_pixel = Pixel(char='.', color=Color(r=100, g=100, b=100))
        fg_pixel = Pixel(char='#', color=Color(r=255, g=0, b=0))
        
        layer1.set_pixel(1, 1, bg_pixel)
        layer2.set_pixel(1, 1, fg_pixel)
        layer2.opacity = 0.5
        
        # Composite
        result = sprite.composite()
        
        # Check result
        composite_pixel = result[1][1]
        assert composite_pixel is not None
        # Foreground should be visible due to higher opacity threshold
        assert composite_pixel.char == '#'


class TestSpriteEditor:
    """Test sprite editor functionality"""
    
    def test_editor_creation(self):
        """Test editor initialization"""
        editor = SpriteEditor()
        
        assert editor.sprite is not None
        assert editor.sprite.name == "New Sprite"
        assert len(editor.sprite.layers) == 1
        assert editor.state.active_tool == "pencil"
    
    def test_tool_selection(self):
        """Test tool switching"""
        editor = SpriteEditor()
        
        editor.set_tool("brush")
        assert editor.state.active_tool == "brush"
        
        editor.set_tool("line")
        assert editor.state.active_tool == "line"
    
    def test_color_management(self):
        """Test color operations"""
        editor = SpriteEditor()
        
        color1 = Color(r=255, g=0, b=0)
        color2 = Color(r=0, g=255, b=0)
        
        editor.set_primary_color(color1)
        editor.set_secondary_color(color2)
        
        assert editor.state.primary_color.r == 255
        assert editor.state.secondary_color.g == 255
        
        # Swap colors
        editor.swap_colors()
        assert editor.state.primary_color.g == 255
        assert editor.state.secondary_color.r == 255
    
    def test_pixel_drawing(self):
        """Test basic pixel drawing"""
        editor = SpriteEditor()
        
        # Draw pixel
        editor.draw_pixel(5, 5, '#')
        
        # Check pixel was drawn
        layer = editor.active_layer
        pixel = layer.get_pixel(5, 5)
        assert pixel is not None
        assert pixel.char == '#'
        assert pixel.color.r == 255  # Default white
    
    def test_drawing_tools(self):
        """Test various drawing tools"""
        editor = SpriteEditor()
        
        # Test line tool
        editor.set_tool("line")
        editor.draw_with_tool(0, 0, 5, 0)
        
        layer = editor.active_layer
        # Check horizontal line
        for x in range(6):
            assert layer.get_pixel(x, 0) is not None
        
        # Test rectangle tool
        editor.set_tool("rectangle")
        editor.draw_with_tool(10, 10, 15, 15)
        
        # Check rectangle corners
        assert layer.get_pixel(10, 10) is not None
        assert layer.get_pixel(15, 15) is not None
        assert layer.get_pixel(10, 15) is not None
        assert layer.get_pixel(15, 10) is not None
    
    def test_fill_tool(self):
        """Test flood fill functionality"""
        editor = SpriteEditor()
        
        # Create a closed shape
        editor.set_tool("rectangle")
        editor.draw_with_tool(5, 5, 10, 10)
        
        # Fill inside
        editor.fill_area(7, 7, '*')
        
        layer = editor.active_layer
        # Check fill worked
        pixel = layer.get_pixel(7, 7)
        assert pixel is not None
        assert pixel.char == '*'
    
    def test_layer_operations(self):
        """Test layer management in editor"""
        editor = SpriteEditor()
        
        # Add layer
        editor.add_layer("Layer2")
        assert len(editor.sprite.layers) == 2
        
        # Switch layers
        editor.set_active_layer(1)
        assert editor.state.active_layer == 1
        
        # Remove layer
        editor.remove_layer(0)
        assert len(editor.sprite.layers) == 1
        assert editor.state.active_layer == 0
    
    def test_undo_redo(self):
        """Test undo/redo functionality"""
        editor = SpriteEditor()
        
        # Draw something
        editor.draw_pixel(5, 5)
        
        # Record history
        assert len(editor.state.history) > 0
        
        # Test undo
        can_undo = editor.undo()
        assert can_undo is True
        
        # Test redo
        can_redo = editor.redo()
        assert can_redo is True
    
    def test_sprite_resize(self):
        """Test sprite resizing"""
        editor = SpriteEditor()
        
        # Draw pixel
        editor.draw_pixel(5, 5)
        
        # Resize
        editor.resize_sprite(64, 64)
        
        assert editor.sprite.width == 64
        assert editor.sprite.height == 64
        
        # Check pixel is preserved
        layer = editor.active_layer
        assert layer.get_pixel(5, 5) is not None


class TestDrawingTools:
    """Test individual drawing tools"""
    
    def test_pencil_tool(self):
        """Test pencil tool (single pixel)"""
        tool = PencilTool()
        points = tool.get_points(0, 0, 5, 5)
        
        assert len(points) == 1
        assert points[0] == (5, 5)
    
    def test_brush_tool(self):
        """Test brush tool (circular area)"""
        tool = BrushTool(size=3)
        points = tool.get_points(0, 0, 10, 10)
        
        # Should create circular area around (10, 10)
        assert len(points) > 1
        assert (10, 10) in points
    
    def test_line_tool(self):
        """Test line drawing"""
        tool = LineTool()
        
        # Horizontal line
        points = tool.get_points(0, 0, 5, 0)
        assert len(points) == 6
        for i in range(6):
            assert (i, 0) in points
        
        # Vertical line
        points = tool.get_points(0, 0, 0, 5)
        assert len(points) == 6
        for i in range(6):
            assert (0, i) in points
    
    def test_rectangle_tool(self):
        """Test rectangle drawing"""
        tool = RectangleTool(filled=False)
        points = tool.get_points(0, 0, 3, 3)
        
        # Check corners
        assert (0, 0) in points
        assert (3, 0) in points
        assert (0, 3) in points
        assert (3, 3) in points
        
        # Check it's not filled
        assert (1, 1) not in points
        assert (2, 2) not in points
        
        # Test filled rectangle
        tool_filled = RectangleTool(filled=True)
        points_filled = tool_filled.get_points(0, 0, 3, 3)
        assert (1, 1) in points_filled
        assert (2, 2) in points_filled
    
    def test_circle_tool(self):
        """Test circle drawing"""
        tool = CircleTool(filled=False)
        points = tool.get_points(5, 5, 8, 5)  # radius 3
        
        # Should have points on circumference
        assert len(points) > 0
        
        # Test filled circle
        tool_filled = CircleTool(filled=True)
        points_filled = tool_filled.get_points(5, 5, 8, 5)
        
        # Filled should have more points
        assert len(points_filled) > len(points)


class TestPalette:
    """Test color palette functionality"""
    
    def test_palette_creation(self):
        """Test palette creation and color management"""
        palette = Palette(name="Test Palette")
        
        assert palette.name == "Test Palette"
        assert len(palette.colors) == 0
        
        # Add colors
        color1 = Color(r=255, g=0, b=0)
        color2 = Color(r=0, g=255, b=0)
        
        palette.add_color(color1)
        palette.add_color(color2)
        
        assert len(palette.colors) == 2
        
        # No duplicates
        palette.add_color(color1)
        assert len(palette.colors) == 2
        
        # Remove color
        palette.remove_color(0)
        assert len(palette.colors) == 1
        assert palette.colors[0].g == 255