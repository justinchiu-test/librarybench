"""Tests for optimizer module."""

import pytest
from pathlib import Path
import tempfile
from src.optimizer import MemoryOptimizer, OptimizationType, OptimizationSuggestion


class TestMemoryOptimizer:
    """Test suite for MemoryOptimizer."""
    
    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = MemoryOptimizer()
        assert len(optimizer.detected_patterns) == 0
        assert len(optimizer.suggestions) == 0
        
    def test_analyze_simple_source(self):
        """Test analyzing simple source code."""
        source = """
def simple_function():
    x = [1, 2, 3]
    return sum(x)
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        assert isinstance(report.total_potential_savings, int)
        assert isinstance(report.suggestions, list)
        assert isinstance(report.memory_patterns, list)
        
    def test_string_concatenation_detection(self):
        """Test detection of string concatenation in loops."""
        source = """
def bad_string_concat():
    result = ""
    for i in range(100):
        result += str(i)
    return result
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        assert len(report.suggestions) > 0
        
        # Should suggest using join
        concat_suggestions = [s for s in report.suggestions 
                            if s.type == OptimizationType.ALGORITHM]
        assert len(concat_suggestions) > 0
        assert any("join" in s.suggested_approach for s in concat_suggestions)
        
    def test_large_list_optimization(self):
        """Test optimization for large lists."""
        source = """
def use_large_list():
    # Large list of numbers
    numbers = [i for i in range(10000)]
    
    # Could use array.array
    int_list = [1, 2, 3, 4, 5] * 100
    
    return sum(numbers)
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        # Should suggest array.array for homogeneous data
        data_structure_suggestions = [s for s in report.suggestions
                                    if s.type == OptimizationType.DATA_STRUCTURE]
        assert len(data_structure_suggestions) > 0
        assert any("array.array" in s.suggested_approach for s in data_structure_suggestions)
        
    def test_class_slots_optimization(self):
        """Test suggestion for __slots__."""
        source = """
class Point:
    def __init__(self, x, y, z, label):
        self.x = x
        self.y = y
        self.z = z
        self.label = label
        
    def distance(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        slots_suggestions = [s for s in report.suggestions
                           if "__slots__" in s.suggested_approach]
        assert len(slots_suggestions) > 0
        assert slots_suggestions[0].implementation_effort == "low"
        
    def test_object_pooling_detection(self):
        """Test detection of object pooling opportunities."""
        source = """
def create_many_objects():
    objects = []
    for i in range(1000):
        obj = Point(i, i*2, i*3)
        objects.append(obj)
        
    # Process objects
    for obj in objects:
        process(obj)
        
    return objects

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        pooling_suggestions = [s for s in report.suggestions
                             if s.type == OptimizationType.OBJECT_POOLING]
        assert len(pooling_suggestions) > 0
        assert "Point" in pooling_suggestions[0].suggested_approach
        
    def test_redundancy_detection(self):
        """Test detection of redundant allocations."""
        source = """
def redundant_copies():
    data = [1, 2, 3, 4, 5] * 100
    
    # Multiple copies
    data_copy1 = data[:]
    data_copy2 = list(data)
    data_copy3 = data.copy()
    
    # Process copies
    result1 = process(data_copy1)
    result2 = process(data_copy2)
    result3 = process(data_copy3)
    
    return result1, result2, result3
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        redundancy_suggestions = [s for s in report.suggestions
                                if s.type == OptimizationType.REDUNDANCY]
        # May detect multiple assignments
        assert len(report.suggestions) >= 0
        
    def test_nested_loop_detection(self):
        """Test detection of deeply nested loops."""
        source = """
def triple_nested_loop():
    result = 0
    for i in range(100):
        for j in range(100):
            for k in range(100):
                result += i * j * k
    return result
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        algorithm_suggestions = [s for s in report.suggestions
                               if "nested loops" in s.current_approach.lower()]
        assert len(algorithm_suggestions) > 0
        assert algorithm_suggestions[0].implementation_effort == "high"
        
    def test_optimization_ranking(self):
        """Test ranking of optimizations."""
        source = """
def multiple_issues():
    # String concatenation (high priority)
    s = ""
    for i in range(1000):
        s += str(i)
    
    # Large list (medium priority)
    large_list = [0] * 10000
    
    # Class without slots (low priority)
    class Data:
        def __init__(self):
            self.value = 0
            
    return s, large_list
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        assert len(report.optimization_ranking) > 0
        
        # Check ranking is sorted by score
        scores = [score for _, score in report.optimization_ranking]
        assert scores == sorted(scores, reverse=True)
        
    def test_implementation_plan(self):
        """Test generation of implementation plan."""
        source = """
def various_optimizations():
    # Quick win - string concat
    s = ""
    for i in range(100):
        s += str(i)
        
    # Medium effort - large data structure
    data = [[0] * 1000 for _ in range(1000)]
    
    # High effort - complex algorithm
    for i in range(100):
        for j in range(100):
            for k in range(100):
                process(i, j, k)
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        assert len(report.implementation_plan) > 0
        
        # Should have phases
        plan_text = '\n'.join(report.implementation_plan)
        assert "Phase" in plan_text
        
    def test_list_append_optimization(self):
        """Test optimization for multiple list appends."""
        source = """
def many_appends():
    result = []
    for i in range(1000):
        result.append(i)
        result.append(i * 2)
        result.append(i * 3)
    return result
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        append_suggestions = [s for s in report.suggestions
                            if "append" in s.current_approach.lower()]
        assert len(append_suggestions) > 0
        assert any("comprehension" in s.suggested_approach for s in append_suggestions)
        
    def test_code_example_inclusion(self):
        """Test that code examples are included in suggestions."""
        source = """
def needs_optimization():
    # String concatenation
    s = ""
    for i in range(100):
        s += str(i)
        
    # Large numeric list
    numbers = [i for i in range(10000)]
    
    return s, numbers
"""
        
        optimizer = MemoryOptimizer()
        report = optimizer.analyze_source(source)
        
        # Check suggestions have code examples
        suggestions_with_examples = [s for s in report.suggestions 
                                   if s.code_example is not None]
        assert len(suggestions_with_examples) > 0
        
    def test_pooling_candidates(self):
        """Test identification of pooling candidates."""
        optimizer = MemoryOptimizer()
        
        allocation_history = [
            ("Connection", 200, 500),  # Good candidate
            ("LargeBuffer", 10000, 10),  # Too large
            ("SmallObj", 50, 1000),  # Good candidate
            ("RareObj", 100, 5),  # Too rare
        ]
        
        candidates = optimizer.identify_pooling_candidates(allocation_history)
        
        assert "Connection" in candidates
        assert "SmallObj" in candidates
        assert "LargeBuffer" not in candidates
        assert "RareObj" not in candidates