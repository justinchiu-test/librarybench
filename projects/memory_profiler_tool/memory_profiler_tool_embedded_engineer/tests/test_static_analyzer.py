"""Tests for static_analyzer module."""

import pytest
from pathlib import Path
import tempfile
from src.static_analyzer import StaticAnalyzer, MemoryEstimate, CodePathAnalysis


class TestStaticAnalyzer:
    """Test suite for StaticAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = StaticAnalyzer()
        assert analyzer.device_memory_limit is None
        
        analyzer_with_limit = StaticAnalyzer(device_memory_limit=1024*1024)
        assert analyzer_with_limit.device_memory_limit == 1024*1024
        
    def test_analyze_simple_source(self):
        """Test analyzing simple Python source."""
        source = """
def simple_function():
    x = [1, 2, 3, 4, 5]
    y = {'a': 1, 'b': 2}
    return x + list(y.values())
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        assert report.total_estimate.min_bytes > 0
        assert report.total_estimate.max_bytes >= report.total_estimate.min_bytes
        assert len(report.code_paths) > 0
        assert len(report.validation_errors) == 0
        
    def test_analyze_with_syntax_error(self):
        """Test handling of syntax errors."""
        source = """
def broken_function(
    # Missing closing parenthesis
    return None
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        assert len(report.validation_errors) > 0
        assert "Syntax error" in report.validation_errors[0]
        
    def test_memory_hotspot_detection(self):
        """Test detection of memory hotspots."""
        source = """
def memory_intensive():
    # Large list
    large_list = [i for i in range(1000)]
    
    # Large dict
    large_dict = {i: str(i) for i in range(500)}
    
    # String concatenation in loop
    result = ""
    for i in range(100):
        result += str(i)
        
    return result
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        assert len(report.memory_hotspots) > 0
        
        # Check for specific hotspots
        hotspot_types = [h[0] for h in report.memory_hotspots]
        assert any("Large list" in h for h in hotspot_types)
        assert any("String concatenation" in h for h in hotspot_types)
        
    def test_list_comprehension_analysis(self):
        """Test analysis of list comprehensions."""
        source = """
def use_comprehensions():
    # Simple list comprehension
    squares = [x**2 for x in range(100)]
    
    # Nested comprehension
    matrix = [[i*j for j in range(10)] for i in range(10)]
    
    # Dict comprehension
    square_dict = {x: x**2 for x in range(50)}
    
    return squares, matrix, square_dict
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should find comprehensions as intensive operations
        for path in report.code_paths:
            if path.path_id.endswith("use_comprehensions:1"):
                assert len(path.intensive_operations) > 0
                assert any("comprehension" in op.lower() for op in path.intensive_operations)
                
    def test_device_memory_validation(self):
        """Test validation against device memory limits."""
        source = """
def allocate_large():
    # Simulate large allocation
    huge_list = [0] * 10000
    huge_dict = {i: i for i in range(5000)}
    return huge_list, huge_dict
"""
        
        # Set a low memory limit
        analyzer = StaticAnalyzer(device_memory_limit=1000)
        report = analyzer.analyze_source(source)
        
        assert len(report.validation_errors) > 0
        assert any("exceeds device limit" in error for error in report.validation_errors)
        
    def test_recommendations_generation(self):
        """Test generation of optimization recommendations."""
        source = """
def inefficient_code():
    # String concatenation in loop
    result = ""
    for i in range(1000):
        result += str(i)
    
    # Nested comprehensions
    nested = [[i*j for j in range(100)] for i in range(100)]
    
    # Large allocation
    big_list = [0] * 100000
    
    return result, nested, big_list
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        assert len(report.recommendations) > 0
        
        # Check for specific recommendations
        rec_text = ' '.join(report.recommendations)
        assert "str.join()" in rec_text or "comprehension" in rec_text
        
    def test_estimate_memory_for_value(self):
        """Test memory estimation for different value types."""
        analyzer = StaticAnalyzer()
        
        # Test various types
        assert analyzer.estimate_memory_for_value(None) == 16
        assert analyzer.estimate_memory_for_value("hello") > 49  # Base + chars
        assert analyzer.estimate_memory_for_value([1, 2, 3]) > 56  # Base + elements
        assert analyzer.estimate_memory_for_value({'a': 1}) > 232  # Base dict size
        assert analyzer.estimate_memory_for_value(b'bytes') > 33  # Base + bytes
        
    def test_analyze_file(self):
        """Test analyzing a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def test_function():
    data = [i for i in range(100)]
    return sum(data)
""")
            f.flush()
            
            analyzer = StaticAnalyzer()
            report = analyzer.analyze_file(Path(f.name))
            
            assert report.total_estimate.min_bytes > 0
            assert len(report.code_paths) > 0
            
            # Clean up
            Path(f.name).unlink()
            
    def test_function_analysis(self):
        """Test detailed function analysis."""
        source = """
def complex_function(n):
    # Multiple allocations
    list1 = [i for i in range(n)]
    list2 = [i**2 for i in list1]
    dict1 = {i: str(i) for i in range(n//2)}
    
    # Function calls
    result = sum(list1) + len(list2)
    
    return result, dict1
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Find the function analysis
        func_analysis = None
        for path in report.code_paths:
            if "complex_function" in path.path_id:
                func_analysis = path
                break
                
        assert func_analysis is not None
        assert len(func_analysis.allocations) > 0
        assert len(func_analysis.function_calls) > 0
        assert 'sum' in func_analysis.function_calls
        
    def test_class_slots_suggestion(self):
        """Test suggestion for using __slots__."""
        source = """
class WithoutSlots:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3
        self.d = 4
        
class WithSlots:
    __slots__ = ['a', 'b']
    
    def __init__(self):
        self.a = 1
        self.b = 2
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should suggest __slots__ for WithoutSlots
        assert any("__slots__" in rec for rec in report.recommendations)
        
    def test_platform_validation(self):
        """Test validation against device profiles."""
        analyzer = StaticAnalyzer()
        
        report = analyzer.analyze_source("x = [1] * 100")
        
        device_profile = {
            'available_memory': 1024,
            'memory_alignment': 4
        }
        
        errors = analyzer.validate_against_device(report, device_profile)
        
        # Check if validation works
        assert isinstance(errors, list)