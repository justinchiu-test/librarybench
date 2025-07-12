"""Tests for the dynamic import optimizer module."""

import tempfile
import os
from datetime import timedelta
from pathlib import Path

import pytest

from import_performance_optimizer.dynamic_optimizer import DynamicImportOptimizer
from import_performance_optimizer.models import DynamicImportSuggestion


class TestDynamicImportOptimizer:
    """Test suite for DynamicImportOptimizer class."""

    def test_optimizer_initialization(self):
        """Test dynamic import optimizer initializes correctly."""
        optimizer = DynamicImportOptimizer()
        assert len(optimizer._function_imports) == 0
        assert len(optimizer._class_imports) == 0
        assert len(optimizer._conditional_imports) == 0
        assert len(optimizer._import_usage_count) == 0

    def test_analyze_function_specific_imports(self):
        """Test analysis of function-specific import usage."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import module1
import module2

def function_a():
    return module1.process()

def function_b():
    return module2.compute()

# Module-level usage
print(module1.VERSION)
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            # Check function-specific tracking
            func_a_key = f"{temp_file}::function_a"
            func_b_key = f"{temp_file}::function_b"
            
            assert 'module1' in optimizer._function_imports.get(func_a_key, set())
            assert 'module2' in optimizer._function_imports.get(func_b_key, set())
            assert optimizer._import_usage_count['module1'] >= 2  # function + module level
        finally:
            os.unlink(temp_file)

    def test_analyze_class_specific_imports(self):
        """Test analysis of class-specific import usage."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import numpy
import pandas

class DataProcessor:
    def process(self):
        return numpy.array([1, 2, 3])
    
    def analyze(self):
        return pandas.DataFrame()
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            class_key = f"{temp_file}::DataProcessor"
            assert 'numpy' in optimizer._class_imports.get(class_key, set())
            assert 'pandas' in optimizer._class_imports.get(class_key, set())
        finally:
            os.unlink(temp_file)

    def test_analyze_conditional_imports(self):
        """Test analysis of conditional import usage."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import heavy_module

if some_condition:
    result = heavy_module.process()
else:
    result = None
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            assert 'heavy_module' in optimizer._conditional_imports
            assert len(optimizer._conditional_imports['heavy_module']) > 0
        finally:
            os.unlink(temp_file)

    def test_generate_suggestions_with_thresholds(self):
        """Test suggestion generation with performance thresholds."""
        optimizer = DynamicImportOptimizer()
        
        # Set up test data
        optimizer._import_usage_count = {
            'slow_module': 5,
            'fast_module': 3,
            'unused_module': 0
        }
        
        optimizer._function_imports = {
            'file.py::slow_function': {'slow_module'}
        }
        
        import_times = {
            'slow_module': 0.1,    # 100ms
            'fast_module': 0.01,   # 10ms
            'unused_module': 0.05  # 50ms
        }
        
        memory_usage = {
            'slow_module': 10 * 1024 * 1024,  # 10MB
            'fast_module': 500 * 1024,        # 500KB
            'unused_module': 5 * 1024 * 1024  # 5MB
        }
        
        optimizer.set_performance_data(import_times, memory_usage)
        
        suggestions = optimizer.generate_suggestions(
            min_time_threshold_ms=50.0,
            min_memory_threshold_mb=1.0
        )
        
        # Should only suggest slow_module (meets both thresholds)
        assert len(suggestions) >= 1
        assert any(s.module_name == 'slow_module' for s in suggestions)
        assert not any(s.module_name == 'fast_module' for s in suggestions)
        assert not any(s.module_name == 'unused_module' for s in suggestions)

    def test_function_import_code_example(self):
        """Test generation of function-level import examples."""
        optimizer = DynamicImportOptimizer()
        
        optimizer._import_usage_count = {'heavy_module': 2}
        optimizer._function_imports = {
            'app.py::process_data': {'heavy_module'}
        }
        
        optimizer.set_performance_data(
            {'heavy_module': 0.5},
            {'heavy_module': 50 * 1024 * 1024}
        )
        
        suggestions = optimizer.generate_suggestions()
        
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        
        assert isinstance(suggestion, DynamicImportSuggestion)
        assert len(suggestion.code_examples) > 0
        assert 'def process_data():' in suggestion.code_examples[0]
        assert 'import heavy_module' in suggestion.code_examples[0]

    def test_conditional_import_code_example(self):
        """Test generation of conditional import examples."""
        optimizer = DynamicImportOptimizer()
        
        optimizer._import_usage_count = {'conditional_module': 1}
        optimizer._conditional_imports = {
            'conditional_module': ['file.py:function']
        }
        
        optimizer.set_performance_data(
            {'conditional_module': 0.3},
            {'conditional_module': 20 * 1024 * 1024}
        )
        
        suggestions = optimizer.generate_suggestions()
        
        assert len(suggestions) == 1
        example = suggestions[0].code_examples[0]
        assert 'if some_condition:' in example
        assert 'import conditional_module' in example

    def test_importlib_code_example(self):
        """Test generation of importlib dynamic import examples."""
        optimizer = DynamicImportOptimizer()
        
        optimizer._import_usage_count = {'dynamic_module': 1}
        
        optimizer.set_performance_data(
            {'dynamic_module': 0.2},
            {'dynamic_module': 15 * 1024 * 1024}
        )
        
        suggestions = optimizer.generate_suggestions()
        
        if suggestions:
            example = suggestions[0].code_examples[0]
            assert 'importlib' in example
            assert 'import_module' in example

    def test_estimated_improvements(self):
        """Test calculation of estimated improvements."""
        optimizer = DynamicImportOptimizer()
        
        optimizer._import_usage_count = {'module': 1}
        optimizer._function_imports = {'file.py::func': {'module'}}
        
        import_time = 1.0  # 1 second
        memory_usage = 100 * 1024 * 1024  # 100MB
        
        optimizer.set_performance_data({'module': import_time}, {'module': memory_usage})
        
        suggestions = optimizer.generate_suggestions()
        
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        
        # Function-specific import should save ~80% of time
        assert suggestion.estimated_time_improvement.total_seconds() == pytest.approx(0.8, rel=0.1)
        assert suggestion.estimated_memory_savings == pytest.approx(80 * 1024 * 1024, rel=0.1)

    def test_optimization_summary(self):
        """Test generation of optimization summary."""
        optimizer = DynamicImportOptimizer()
        
        # Set up multiple optimization opportunities
        optimizer._import_usage_count = {
            'module1': 2,
            'module2': 1,
            'module3': 3
        }
        
        optimizer._function_imports = {
            'file.py::func1': {'module1'},
            'file.py::func2': {'module2'}
        }
        
        optimizer._conditional_imports = {
            'module3': ['file.py:conditional_block']
        }
        
        optimizer.set_performance_data(
            {
                'module1': 0.5,
                'module2': 0.3,
                'module3': 0.4
            },
            {
                'module1': 50 * 1024 * 1024,
                'module2': 30 * 1024 * 1024,
                'module3': 40 * 1024 * 1024
            }
        )
        
        summary = optimizer.get_optimization_summary()
        
        assert 'total_suggestions' in summary
        assert 'total_time_savings_seconds' in summary
        assert 'total_memory_savings_mb' in summary
        assert 'function_specific_count' in summary
        assert 'conditional_import_count' in summary
        assert summary['total_suggestions'] >= 3

    def test_complex_usage_patterns(self):
        """Test analysis of complex usage patterns."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import module1
from module2 import func as module2_func
import module3.submodule as sub

class MyClass:
    def method1(self):
        return module1.process()
    
    def method2(self):
        if condition:
            return module2_func()
        else:
            return sub.compute()

def standalone_function():
    return module1.helper() + sub.value
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            assert optimizer._import_usage_count['module1'] >= 2
            assert optimizer._import_usage_count['module2_func'] >= 1
            assert optimizer._import_usage_count['sub'] >= 2
        finally:
            os.unlink(temp_file)

    def test_nested_function_handling(self):
        """Test handling of nested functions."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import outer_module

def outer_function():
    def inner_function():
        return outer_module.process()
    
    return inner_function()
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            # Should track usage in outer function
            func_key = f"{temp_file}::outer_function"
            assert 'outer_module' in optimizer._function_imports.get(func_key, set())
        finally:
            os.unlink(temp_file)

    def test_async_function_handling(self):
        """Test handling of async functions."""
        optimizer = DynamicImportOptimizer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import async_module

async def async_function():
    return await async_module.async_process()
""")
            temp_file = f.name
        
        try:
            optimizer.analyze_file(temp_file)
            
            func_key = f"{temp_file}::async_function"
            assert 'async_module' in optimizer._function_imports.get(func_key, set())
        finally:
            os.unlink(temp_file)

    def test_performance_requirements(self):
        """Test optimizer meets performance requirements."""
        import time
        
        optimizer = DynamicImportOptimizer()
        
        # Create a large test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import module1\n" * 100)
            f.write("\n")
            for i in range(1000):
                f.write(f"def func_{i}():\n    return module1.process()\n\n")
            temp_file = f.name
        
        try:
            start_time = time.perf_counter()
            optimizer.analyze_file(temp_file)
            elapsed = time.perf_counter() - start_time
            
            # Should analyze large file quickly
            assert elapsed < 5.0
        finally:
            os.unlink(temp_file)

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        optimizer = DynamicImportOptimizer()
        
        # Test with no imports
        suggestions = optimizer.generate_suggestions()
        assert suggestions == []
        
        # Test with malformed file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("This is not valid Python {{{")
            temp_file = f.name
        
        try:
            # Should not raise exception
            optimizer.analyze_file(temp_file)
        finally:
            os.unlink(temp_file)
        
        # Test with non-existent file
        optimizer.analyze_file("/non/existent/file.py")  # Should not raise