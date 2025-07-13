"""Tests for the lazy loading detector module."""

import tempfile
import os
from datetime import timedelta
from pathlib import Path

import pytest

from import_performance_optimizer.lazy_loading import LazyLoadingDetector
from import_performance_optimizer.models import LazyLoadingOpportunity


class TestLazyLoadingDetector:
    """Test suite for LazyLoadingDetector class."""

    def test_detector_initialization(self):
        """Test lazy loading detector initializes correctly."""
        detector = LazyLoadingDetector()
        assert detector._module_usage == {}
        assert detector._import_locations == {}
        assert detector._module_import_times == {}

    def test_analyze_file_with_imports(self):
        """Test analyzing a Python file for imports."""
        detector = LazyLoadingDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
import sys
from pathlib import Path

def my_function():
    return os.path.join('a', 'b')

class MyClass:
    def method(self):
        return sys.version
""")
            temp_file = f.name
        
        try:
            detector.analyze_file(temp_file)
            
            assert 'os' in detector._import_locations
            assert 'sys' in detector._import_locations
            assert 'pathlib' in detector._import_locations
        finally:
            os.unlink(temp_file)

    def test_analyze_directory(self):
        """Test analyzing all Python files in a directory."""
        detector = LazyLoadingDetector()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = Path(temp_dir) / "test1.py"
            file1.write_text("import os\nprint(os.name)")
            
            file2 = Path(temp_dir) / "test2.py"
            file2.write_text("import sys\nprint(sys.version)")
            
            detector.analyze_directory(temp_dir)
            
            assert 'os' in detector._import_locations
            assert 'sys' in detector._import_locations

    def test_detect_unused_imports(self):
        """Test detection of unused imports."""
        detector = LazyLoadingDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import unused_module
import used_module

def function():
    return used_module.something()
""")
            temp_file = f.name
        
        try:
            detector.analyze_file(temp_file)
            detector.set_module_import_times({
                'unused_module': 0.1,
                'used_module': 0.05
            })
            
            opportunities = detector.detect_opportunities()
            
            unused_opps = [o for o in opportunities if o.first_usage_location is None]
            assert len(unused_opps) >= 1
            assert any(o.module_name == 'unused_module' for o in unused_opps)
        finally:
            os.unlink(temp_file)

    def test_detect_delayed_usage(self):
        """Test detection of imports with delayed usage."""
        detector = LazyLoadingDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import heavy_module

# 100 lines of other code
""" + "\n" * 100 + """
def much_later():
    return heavy_module.process()
""")
            temp_file = f.name
        
        try:
            detector.analyze_file(temp_file)
            detector.set_module_import_times({'heavy_module': 0.5})
            
            opportunities = detector.detect_opportunities(min_usage_delay_lines=50)
            
            assert len(opportunities) >= 1
            assert opportunities[0].confidence_score > 0.5
        finally:
            os.unlink(temp_file)

    def test_transformation_suggestions(self):
        """Test generation of transformation suggestions."""
        detector = LazyLoadingDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import numpy
import pandas.dataframe

def compute():
    return numpy.array([1, 2, 3])
""")
            temp_file = f.name
        
        try:
            detector.analyze_file(temp_file)
            detector.set_module_import_times({
                'numpy': 0.2,
                'pandas.dataframe': 0.3
            })
            
            opportunities = detector.detect_opportunities()
            
            for opp in opportunities:
                assert isinstance(opp.transformation_suggestion, str)
                assert len(opp.transformation_suggestion) > 0
        finally:
            os.unlink(temp_file)

    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        detector = LazyLoadingDetector()
        
        # Test various scenarios
        scenarios = [
            # (import_line, usage_line, expected_confidence_range)
            (1, 10, (0.0, 0.5)),      # Close usage
            (1, 100, (0.5, 0.9)),     # Delayed usage
            (1, None, (0.8, 1.0)),    # Unused import
        ]
        
        for import_line, usage_line, confidence_range in scenarios:
            detector._import_locations = {'test_module': ('test.py', import_line)}
            if usage_line:
                detector._module_usage = {'test_module': [('test.py', usage_line)]}
            else:
                detector._module_usage = {}
            
            detector.set_module_import_times({'test_module': 0.1})
            opportunities = detector.detect_opportunities(min_usage_delay_lines=20)
            
            if opportunities:
                confidence = opportunities[0].confidence_score
                assert confidence_range[0] <= confidence <= confidence_range[1]

    def test_summary_report(self):
        """Test generation of summary report."""
        detector = LazyLoadingDetector()
        detector._import_locations = {
            'module1': ('file1.py', 1),
            'module2': ('file2.py', 1),
            'module3': ('file3.py', 1)
        }
        detector._module_usage = {
            'module1': [('file1.py', 100)],
            'module2': [('file2.py', 50)]
            # module3 is unused
        }
        detector.set_module_import_times({
            'module1': 0.5,
            'module2': 0.3,
            'module3': 0.2
        })
        
        report = detector.get_summary_report()
        
        assert 'total_opportunities' in report
        assert 'total_time_savings_seconds' in report
        assert 'unused_imports_count' in report
        assert report['unused_imports_count'] >= 1

    def test_multi_file_usage_tracking(self):
        """Test tracking module usage across multiple files."""
        detector = LazyLoadingDetector()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # File 1: imports module
            file1 = Path(temp_dir) / "importer.py"
            file1.write_text("import shared_module")
            
            # File 2: uses module
            file2 = Path(temp_dir) / "user.py"
            file2.write_text("""
import shared_module

def use_it():
    return shared_module.function()
""")
            
            detector.analyze_directory(temp_dir)
            
            assert 'shared_module' in detector._import_locations

    def test_complex_import_patterns(self):
        """Test handling of complex import patterns."""
        detector = LazyLoadingDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import module1
from module2 import func1, func2
from module3 import Class1 as MyClass
import module4.submodule

# Usage patterns
result1 = module1.process()
result2 = func1()
obj = MyClass()
result4 = module4.submodule.method()
""")
            temp_file = f.name
        
        try:
            detector.analyze_file(temp_file)
            
            assert 'module1' in detector._import_locations
            assert 'module2' in detector._import_locations
            assert 'module3' in detector._import_locations
            assert 'module4.submodule' in detector._import_locations
        finally:
            os.unlink(temp_file)

    def test_performance_thresholds(self):
        """Test performance threshold filtering."""
        detector = LazyLoadingDetector()
        detector._import_locations = {
            'slow_module': ('file.py', 1),
            'fast_module': ('file.py', 2)
        }
        detector.set_module_import_times({
            'slow_module': 0.1,    # 100ms
            'fast_module': 0.005   # 5ms
        })
        
        # Only slow imports should be flagged
        opportunities = detector.detect_opportunities(min_import_time_ms=10.0)
        
        module_names = [o.module_name for o in opportunities]
        assert 'slow_module' in module_names
        assert 'fast_module' not in module_names

    def test_estimated_time_savings(self):
        """Test calculation of estimated time savings."""
        detector = LazyLoadingDetector()
        detector._import_locations = {'heavy_module': ('file.py', 1)}
        detector._module_usage = {}  # Unused
        detector.set_module_import_times({'heavy_module': 1.0})  # 1 second
        
        opportunities = detector.detect_opportunities()
        
        assert len(opportunities) == 1
        assert opportunities[0].estimated_time_savings.total_seconds() > 0
        assert opportunities[0].estimated_time_savings.total_seconds() <= 1.0

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        detector = LazyLoadingDetector()
        
        # Test with malformed Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("This is not valid Python syntax {{{")
            temp_file = f.name
        
        try:
            # Should not raise exception
            detector.analyze_file(temp_file)
        finally:
            os.unlink(temp_file)
        
        # Test with no imports
        opportunities = detector.detect_opportunities()
        assert opportunities == []
        
        # Test with empty directory
        with tempfile.TemporaryDirectory() as temp_dir:
            detector.analyze_directory(temp_dir)
            # Should not raise exception