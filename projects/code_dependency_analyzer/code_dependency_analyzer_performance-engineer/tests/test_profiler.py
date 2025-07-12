"""Tests for the import profiler module."""

import time
import sys
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest

from import_performance_optimizer.profiler import ImportProfiler
from import_performance_optimizer.models import ImportMetrics


class TestImportProfiler:
    """Test suite for ImportProfiler class."""

    def test_profiler_initialization(self):
        """Test profiler initializes correctly."""
        profiler = ImportProfiler()
        assert profiler._import_times == {}
        assert profiler._import_tree == {}
        assert profiler._import_stack == []
        assert profiler._is_profiling is False

    def test_start_stop_profiling(self):
        """Test starting and stopping profiling."""
        profiler = ImportProfiler()
        import builtins
        original_import = builtins.__import__
        
        profiler.start_profiling()
        assert profiler._is_profiling is True
        assert builtins.__import__ != original_import
        
        profiler.stop_profiling()
        assert profiler._is_profiling is False
        assert builtins.__import__ == original_import

    def test_profile_context_manager(self):
        """Test profile context manager."""
        profiler = ImportProfiler()
        
        with profiler.profile():
            assert profiler._is_profiling is True
        
        assert profiler._is_profiling is False

    @patch('time.perf_counter')
    def test_profiled_import(self, mock_perf_counter):
        """Test import profiling captures timing."""
        mock_perf_counter.side_effect = [0.0, 0.1, 0.1, 0.3]
        
        profiler = ImportProfiler()
        profiler._original_import = MagicMock(return_value=MagicMock())
        
        result = profiler._profiled_import('test_module')
        
        assert 'test_module' in profiler._import_times
        assert profiler._import_times['test_module'] == 0.1
        
        result2 = profiler._profiled_import('test_module2')
        assert profiler._import_times['test_module2'] == pytest.approx(0.2)

    def test_import_tree_building(self):
        """Test import dependency tree building."""
        profiler = ImportProfiler()
        profiler._original_import = MagicMock(return_value=MagicMock())
        
        profiler._import_stack = []
        profiler._profiled_import('parent_module')
        
        profiler._import_stack = ['parent_module']
        profiler._profiled_import('child_module')
        
        assert 'child_module' in profiler._import_tree['parent_module']

    def test_get_import_metrics(self):
        """Test getting detailed import metrics."""
        profiler = ImportProfiler()
        profiler._import_times = {
            'module_a': 0.5,
            'module_b': 0.3,
            'module_c': 0.8
        }
        profiler._import_tree = {
            'module_a': ['module_b'],
            'module_b': ['module_c']
        }
        profiler._import_depths = {
            'module_a': 0,
            'module_b': 1,
            'module_c': 2
        }
        
        metrics = profiler.get_import_metrics()
        
        assert len(metrics) == 3
        assert all(isinstance(m, ImportMetrics) for m in metrics)
        assert metrics[0].cumulative_time >= metrics[0].import_time

    def test_identify_bottlenecks(self):
        """Test bottleneck identification."""
        profiler = ImportProfiler()
        cumulative_times = {
            'slow_module': 2.0,
            'medium_module': 0.5,
            'fast_module': 0.1
        }
        
        bottlenecks = profiler._identify_bottlenecks(cumulative_times, 0.7)
        
        assert 'slow_module' in bottlenecks
        assert 'fast_module' not in bottlenecks

    def test_get_slowest_imports(self):
        """Test getting slowest imports."""
        profiler = ImportProfiler()
        profiler._import_times = {
            'slow_1': 1.0,
            'slow_2': 0.8,
            'medium': 0.5,
            'fast': 0.1
        }
        
        slowest = profiler.get_slowest_imports(top_n=2)
        
        assert len(slowest) == 2
        assert slowest[0][0] == 'slow_1'
        assert slowest[1][0] == 'slow_2'
        assert isinstance(slowest[0][1], timedelta)

    def test_import_tree_visualization(self):
        """Test import tree visualization generation."""
        profiler = ImportProfiler()
        profiler._import_times = {
            'root': 0.5,
            'child1': 0.3,
            'child2': 0.2
        }
        profiler._import_tree = {
            'root': ['child1', 'child2']
        }
        
        visualization = profiler.get_import_tree_visualization()
        
        assert 'root' in visualization
        assert 'child1' in visualization
        assert 'child2' in visualization
        assert '0.500s' in visualization

    def test_circular_import_handling(self):
        """Test handling of circular imports in visualization."""
        profiler = ImportProfiler()
        profiler._import_times = {
            'module_a': 0.5,
            'module_b': 0.3
        }
        profiler._import_tree = {
            'module_a': ['module_b'],
            'module_b': ['module_a']
        }
        
        visualization = profiler.get_import_tree_visualization()
        
        assert 'circular' in visualization

    def test_clear_profiling_data(self):
        """Test clearing all profiling data."""
        profiler = ImportProfiler()
        profiler._import_times = {'test': 0.1}
        profiler._import_tree = {'test': ['child']}
        profiler._import_stack = ['test']
        
        profiler.clear()
        
        assert profiler._import_times == {}
        assert len(profiler._import_tree) == 0
        assert profiler._import_stack == []

    def test_concurrent_profiling(self):
        """Test thread-safe profiling."""
        import threading
        
        profiler = ImportProfiler()
        profiler._original_import = MagicMock(return_value=MagicMock())
        
        def import_module(name):
            profiler._profiled_import(name)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=import_module, args=(f'module_{i}',))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(profiler._import_times) == 5

    def test_microsecond_precision(self):
        """Test import time measurement with microsecond precision."""
        profiler = ImportProfiler()
        profiler._import_times = {
            'fast_module': 0.000123,  # 123 microseconds
            'slower_module': 0.001234  # 1.234 milliseconds
        }
        
        metrics = profiler.get_import_metrics()
        
        fast_metric = next(m for m in metrics if m.module_name == 'fast_module')
        assert fast_metric.import_time.total_seconds() == pytest.approx(0.000123, rel=1e-6)

    def test_performance_benchmarks(self):
        """Test profiler meets performance requirements."""
        profiler = ImportProfiler()
        profiler._original_import = MagicMock(return_value=MagicMock())
        
        start_time = time.perf_counter()
        
        for i in range(1000):
            profiler._profiled_import(f'module_{i}')
        
        elapsed = time.perf_counter() - start_time
        
        # Should complete 1000 imports with less than 50ms overhead
        assert elapsed < 0.05

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        profiler = ImportProfiler()
        
        # Test empty metrics
        metrics = profiler.get_import_metrics()
        assert metrics == []
        
        # Test stopping when not started
        profiler.stop_profiling()  # Should not raise
        
        # Test double start
        profiler.start_profiling()
        profiler.start_profiling()  # Should not raise
        profiler.stop_profiling()