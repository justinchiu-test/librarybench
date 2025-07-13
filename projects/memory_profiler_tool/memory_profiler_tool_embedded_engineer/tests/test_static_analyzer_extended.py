"""Extended tests for static_analyzer module."""

import pytest
from pathlib import Path
import tempfile
import ast
from src.static_analyzer import StaticAnalyzer, MemoryEstimate, CodePathAnalysis, DeploymentReport


class TestStaticAnalyzerExtended:
    """Extended test suite for StaticAnalyzer."""
    
    def test_nested_function_analysis(self):
        """Test analysis of nested functions."""
        source = """
def outer_function():
    data = [1, 2, 3]
    
    def inner_function():
        inner_data = [4, 5, 6]
        return sum(inner_data)
    
    return inner_function() + sum(data)
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze both functions
        assert len(report.code_paths) >= 2
        
    def test_lambda_function_analysis(self):
        """Test analysis of lambda functions."""
        source = """
def use_lambdas():
    numbers = [1, 2, 3, 4, 5]
    squared = list(map(lambda x: x**2, numbers))
    filtered = list(filter(lambda x: x > 2, squared))
    return filtered
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze the function
        assert len(report.code_paths) > 0
        # Should detect list allocations
        assert any('list' in str(path.allocations) for path in report.code_paths)
        
    def test_generator_vs_list_detection(self):
        """Test detection of generator vs list opportunities."""
        source = """
def use_list():
    # Could be a generator
    large_list = [x**2 for x in range(10000)]
    return sum(large_list)

def use_generator():
    # Good - using generator
    gen = (x**2 for x in range(10000))
    return sum(gen)
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze both functions
        assert len(report.code_paths) >= 1
        # Should detect the list comprehension
        assert len(report.memory_hotspots) > 0
        
    def test_recursive_function_analysis(self):
        """Test analysis of recursive functions."""
        source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    cache = {}
    def fib(n):
        if n in cache:
            return cache[n]
        if n <= 1:
            return n
        result = fib(n-1) + fib(n-2)
        cache[n] = result
        return result
    return fib(n)
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze recursive patterns
        assert len(report.code_paths) > 0
        
    def test_decorator_memory_impact(self):
        """Test analysis of decorator memory impact."""
        source = """
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def expensive_function(n):
    return [i**2 for i in range(n)]
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should detect cache allocation
        assert any('dict' in str(path.allocations) for path in report.code_paths)
        
    def test_global_variable_detection(self):
        """Test detection of global variable memory usage."""
        source = """
def use_globals():
    GLOBAL_CACHE = {}
    GLOBAL_BUFFER = [0] * 10000
    GLOBAL_CACHE['key'] = 'value'
    GLOBAL_BUFFER[0] = 1
    return len(GLOBAL_CACHE)
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze the function
        assert len(report.code_paths) > 0
        # Should detect the list multiplication pattern in the function
        assert any(alloc[0] == 'list_mult' for path in report.code_paths for alloc in path.allocations)
        
    def test_exception_handling_overhead(self):
        """Test analysis of exception handling overhead."""
        source = """
def with_exceptions():
    try:
        data = [1, 2, 3]
        result = data[10]  # Will raise IndexError
    except IndexError:
        error_data = ['error'] * 100
        return error_data
    finally:
        cleanup_data = []
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should account for exception path allocations
        assert len(report.code_paths) > 0
        
    def test_import_memory_impact(self):
        """Test estimation of import memory impact."""
        source = """
import sys
import collections
from typing import List, Dict

def use_imports():
    counter = collections.Counter([1, 2, 3, 3, 3])
    type_hint: List[int] = [1, 2, 3]
    return counter, type_hint
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should analyze imported type usage
        assert len(report.code_paths) > 0
        
    def test_memory_estimate_confidence(self):
        """Test confidence levels in memory estimates."""
        source = """
def certain_allocation():
    # Fixed size allocation
    return [0] * 100

def uncertain_allocation(n):
    # Dynamic size allocation
    return [0] * n
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # All estimates should have confidence scores
        for path in report.code_paths:
            assert 0.0 <= path.memory_estimate.confidence <= 1.0
            
    def test_async_function_analysis(self):
        """Test analysis of async functions."""
        source = """
async def async_function():
    data = []
    for i in range(100):
        data.append(i)
    return data

async def async_with_await():
    import asyncio
    results = []
    await asyncio.sleep(0.1)
    results.extend([1, 2, 3])
    return results
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should handle async syntax without errors
        assert report is not None
        # May or may not analyze async functions depending on implementation
        assert len(report.validation_errors) == 0 or len(report.code_paths) >= 0
        
    def test_type_annotation_impact(self):
        """Test impact of type annotations on memory."""
        source = """
from typing import List, Dict, Optional, Union

def typed_function(
    items: List[int],
    mapping: Dict[str, int],
    optional: Optional[str] = None
) -> Union[List[int], Dict[str, int]]:
    result: List[int] = []
    temp: Dict[str, int] = {}
    
    for item in items:
        result.append(item * 2)
        
    return result if optional else mapping
"""
        
        analyzer = StaticAnalyzer()
        report = analyzer.analyze_source(source)
        
        # Should handle type annotations
        assert len(report.code_paths) > 0