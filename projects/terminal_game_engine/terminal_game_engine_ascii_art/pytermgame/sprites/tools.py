"""Drawing tools for sprite editor"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Set
import math

from .models import Layer, Pixel


class DrawingTool(ABC):
    """Base drawing tool"""
    
    def __init__(self):
        self.default_char = '#'
    
    @abstractmethod
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points affected by tool"""
        pass


class PencilTool(DrawingTool):
    """Single pixel pencil tool"""
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points for pencil (single pixel)"""
        return [(end_x, end_y)]


class BrushTool(DrawingTool):
    """Multi-pixel brush tool"""
    
    def __init__(self, size: int = 3):
        super().__init__()
        self.size = size
        self.default_char = '*'
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points for brush (circle around cursor)"""
        points = []
        radius = self.size // 2
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    points.append((end_x + dx, end_y + dy))
        
        return points


class LineTool(DrawingTool):
    """Line drawing tool"""
    
    def __init__(self):
        super().__init__()
        self.default_char = '-'
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points for line (Bresenham's algorithm)"""
        points = []
        
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        x, y = start_x, start_y
        
        x_inc = 1 if start_x < end_x else -1
        y_inc = 1 if start_y < end_y else -1
        
        if dx > dy:
            error = dx / 2.0
            while x != end_x:
                points.append((x, y))
                error -= dy
                if error < 0:
                    y += y_inc
                    error += dx
                x += x_inc
        else:
            error = dy / 2.0
            while y != end_y:
                points.append((x, y))
                error -= dx
                if error < 0:
                    x += x_inc
                    error += dy
                y += y_inc
        
        points.append((end_x, end_y))
        return points


class RectangleTool(DrawingTool):
    """Rectangle drawing tool"""
    
    def __init__(self, filled: bool = False):
        super().__init__()
        self.filled = filled
        self.default_char = '#'
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points for rectangle"""
        points = []
        
        min_x = min(start_x, end_x)
        max_x = max(start_x, end_x)
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        
        if self.filled:
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    points.append((x, y))
        else:
            # Top and bottom edges
            for x in range(min_x, max_x + 1):
                points.append((x, min_y))
                points.append((x, max_y))
            
            # Left and right edges (excluding corners)
            for y in range(min_y + 1, max_y):
                points.append((min_x, y))
                points.append((max_x, y))
        
        return points


class CircleTool(DrawingTool):
    """Circle drawing tool"""
    
    def __init__(self, filled: bool = False):
        super().__init__()
        self.filled = filled
        self.default_char = 'o'
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Get points for circle"""
        points = []
        
        # Calculate radius from start to end point
        radius = int(math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2))
        
        if self.filled:
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if x * x + y * y <= radius * radius:
                        points.append((start_x + x, start_y + y))
        else:
            # Bresenham's circle algorithm
            x = 0
            y = radius
            d = 3 - 2 * radius
            
            while x <= y:
                # Add 8 symmetric points
                points.extend([
                    (start_x + x, start_y + y),
                    (start_x - x, start_y + y),
                    (start_x + x, start_y - y),
                    (start_x - x, start_y - y),
                    (start_x + y, start_y + x),
                    (start_x - y, start_y + x),
                    (start_x + y, start_y - x),
                    (start_x - y, start_y - x),
                ])
                
                if d > 0:
                    y -= 1
                    d += 4 * (x - y) + 10
                else:
                    d += 4 * x + 6
                
                x += 1
        
        # Remove duplicates
        return list(set(points))


class FillTool(DrawingTool):
    """Flood fill tool"""
    
    def __init__(self):
        super().__init__()
        self.default_char = '#'
    
    def get_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """Fill tool doesn't use start/end points in the same way"""
        return [(end_x, end_y)]
    
    def get_fill_points(self, layer: Layer, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all points to fill using flood fill algorithm"""
        if not (0 <= x < layer.width and 0 <= y < layer.height):
            return []
        
        target_pixel = layer.get_pixel(x, y)
        points: Set[Tuple[int, int]] = set()
        stack = [(x, y)]
        
        while stack:
            cx, cy = stack.pop()
            
            if (cx, cy) in points:
                continue
            
            if not (0 <= cx < layer.width and 0 <= cy < layer.height):
                continue
            
            current_pixel = layer.get_pixel(cx, cy)
            
            # Check if pixel matches target
            if self._pixels_match(current_pixel, target_pixel):
                points.add((cx, cy))
                
                # Add adjacent pixels
                stack.extend([
                    (cx + 1, cy),
                    (cx - 1, cy),
                    (cx, cy + 1),
                    (cx, cy - 1),
                ])
        
        return list(points)
    
    def _pixels_match(self, p1: Optional[Pixel], p2: Optional[Pixel]) -> bool:
        """Check if two pixels match for fill purposes"""
        if p1 is None and p2 is None:
            return True
        if p1 is None or p2 is None:
            return False
        return (p1.char == p2.char and 
                p1.color.r == p2.color.r and
                p1.color.g == p2.color.g and
                p1.color.b == p2.color.b)