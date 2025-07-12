"""Tests for the circular import analyzer module."""

from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest

from import_performance_optimizer.circular_imports import CircularImportAnalyzer
from import_performance_optimizer.models import CircularImportInfo


class TestCircularImportAnalyzer:
    """Test suite for CircularImportAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test circular import analyzer initializes correctly."""
        analyzer = CircularImportAnalyzer()
        assert len(analyzer._import_graph) == 0
        assert analyzer._circular_imports == []
        assert analyzer._import_times == {}
        assert analyzer._import_memory == {}

    def test_build_import_graph(self):
        """Test building import dependency graph."""
        analyzer = CircularImportAnalyzer()
        
        # Mock the module analysis
        analyzer._import_graph = {
            'module_a': {'module_b', 'module_c'},
            'module_b': {'module_c'},
            'module_c': set()
        }
        
        analyzer._detect_circular_imports()
        
        # No circular imports in this graph
        assert len(analyzer._circular_imports) == 0

    def test_detect_simple_circular_import(self):
        """Test detection of simple circular import (A -> B -> A)."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._import_graph = {
            'module_a': {'module_b'},
            'module_b': {'module_a'}
        }
        
        analyzer._detect_circular_imports()
        
        assert len(analyzer._circular_imports) >= 1
        cycle = analyzer._circular_imports[0]
        assert set(cycle) == {'module_a', 'module_b'}

    def test_detect_complex_circular_import(self):
        """Test detection of complex circular import (A -> B -> C -> A)."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._import_graph = {
            'module_a': {'module_b'},
            'module_b': {'module_c'},
            'module_c': {'module_a'}
        }
        
        analyzer._detect_circular_imports()
        
        assert len(analyzer._circular_imports) >= 1
        cycle = analyzer._circular_imports[0]
        assert len(cycle) == 4  # Includes repeated module
        assert 'module_a' in cycle
        assert 'module_b' in cycle
        assert 'module_c' in cycle

    def test_measure_circular_import_impact(self):
        """Test measuring performance impact of circular imports."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._circular_imports = [
            ['module_a', 'module_b', 'module_a'],
            ['module_x', 'module_y', 'module_z', 'module_x']
        ]
        
        import_times = {
            'module_a': 0.5,
            'module_b': 0.3,
            'module_x': 0.2,
            'module_y': 0.1,
            'module_z': 0.15
        }
        
        memory_usage = {
            'module_a': 5 * 1024 * 1024,  # 5MB
            'module_b': 3 * 1024 * 1024,  # 3MB
            'module_x': 2 * 1024 * 1024,  # 2MB
            'module_y': 1 * 1024 * 1024,  # 1MB
            'module_z': 1 * 1024 * 1024   # 1MB
        }
        
        infos = analyzer.measure_circular_import_impact(import_times, memory_usage)
        
        assert len(infos) == 2
        assert all(isinstance(info, CircularImportInfo) for info in infos)
        
        # Check performance impact calculation (20% overhead)
        first_impact = infos[0].performance_impact.total_seconds()
        assert first_impact > 0

    def test_severity_determination(self):
        """Test severity level determination for circular imports."""
        analyzer = CircularImportAnalyzer()
        
        test_cases = [
            # (time_impact, memory_overhead, cycle_length, expected_severity)
            (0.05, 500 * 1024, 2, "low"),              # Small impact
            (0.5, 5 * 1024 * 1024, 3, "medium"),       # Medium impact
            (1.0, 10 * 1024 * 1024, 4, "high"),        # High impact
            (2.0, 15 * 1024 * 1024, 6, "critical"),    # Critical impact
        ]
        
        for time_impact, memory_overhead, cycle_length, expected in test_cases:
            severity = analyzer._determine_severity(time_impact, memory_overhead, cycle_length)
            assert severity == expected

    def test_import_chain_building(self):
        """Test building readable import chain."""
        analyzer = CircularImportAnalyzer()
        
        cycle = ['module_a', 'module_b', 'module_c']
        chain = analyzer._build_import_chain(cycle)
        
        assert len(chain) == 3
        assert chain[0] == 'module_a -> module_b'
        assert chain[1] == 'module_b -> module_c'
        assert chain[2] == 'module_c -> module_a'

    def test_find_all_circular_paths(self):
        """Test finding all circular paths between modules."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._import_graph = {
            'a': {'b', 'c'},
            'b': {'d'},
            'c': {'d'},
            'd': {'a'}
        }
        
        paths = analyzer.find_all_circular_paths('a', 'a')
        
        assert len(paths) >= 2  # At least two paths: a->b->d->a and a->c->d->a

    def test_refactoring_suggestions(self):
        """Test generation of refactoring suggestions."""
        analyzer = CircularImportAnalyzer()
        
        circular_info = CircularImportInfo(
            modules_involved=['module_a', 'module_b', 'module_c', 'module_d', 'module_a'],
            performance_impact=timedelta(seconds=1.5),
            memory_overhead=10 * 1024 * 1024,
            import_chain=['module_a -> module_b', 'module_b -> module_c', 
                         'module_c -> module_d', 'module_d -> module_a'],
            severity="high"
        )
        
        suggestions = analyzer.get_refactoring_suggestions(circular_info)
        
        assert len(suggestions) > 0
        assert any('dependency injection' in s for s in suggestions)
        assert any('URGENT' in s for s in suggestions)

    def test_summary_report(self):
        """Test generation of summary report."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._circular_imports = [
            ['a', 'b', 'a'],
            ['x', 'y', 'z', 'x']
        ]
        
        analyzer._import_times = {
            'a': 0.5, 'b': 0.3,
            'x': 0.2, 'y': 0.1, 'z': 0.15
        }
        
        analyzer._import_memory = {
            'a': 5 * 1024 * 1024, 'b': 3 * 1024 * 1024,
            'x': 2 * 1024 * 1024, 'y': 1 * 1024 * 1024, 'z': 1 * 1024 * 1024
        }
        
        report = analyzer.get_summary_report()
        
        assert 'total_circular_imports' in report
        assert 'critical_severity_count' in report
        assert 'total_time_impact_seconds' in report
        assert 'total_memory_overhead_bytes' in report
        assert report['total_circular_imports'] == 2

    def test_multiple_cycles_same_modules(self):
        """Test handling multiple cycles involving same modules."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._import_graph = {
            'a': {'b', 'c'},
            'b': {'a'},
            'c': {'a'}
        }
        
        analyzer._detect_circular_imports()
        
        # Should detect both cycles: a->b->a and a->c->a
        assert len(analyzer._circular_imports) >= 2

    def test_self_import_detection(self):
        """Test detection of self-imports."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._import_graph = {
            'module_self': {'module_self'}
        }
        
        analyzer._detect_circular_imports()
        
        assert len(analyzer._circular_imports) >= 1

    def test_performance_overhead_calculation(self):
        """Test accurate calculation of performance overhead."""
        analyzer = CircularImportAnalyzer()
        
        cycle = ['module_a', 'module_b']
        analyzer._import_times = {
            'module_a': 1.0,
            'module_b': 0.5
        }
        
        # 20% overhead factor
        impact = analyzer._calculate_time_impact(cycle)
        expected = (1.0 + 0.5) * 0.2  # 20% of total time
        assert impact == pytest.approx(expected)

    def test_memory_overhead_calculation(self):
        """Test accurate calculation of memory overhead."""
        analyzer = CircularImportAnalyzer()
        
        cycle = ['module_a', 'module_b']
        analyzer._import_memory = {
            'module_a': 10 * 1024 * 1024,  # 10MB
            'module_b': 5 * 1024 * 1024    # 5MB
        }
        
        # 10% overhead factor
        overhead = analyzer._calculate_memory_overhead(cycle)
        expected = int((10 + 5) * 1024 * 1024 * 0.1)  # 10% of total memory
        assert overhead == expected

    def test_empty_graph_handling(self):
        """Test handling of empty import graph."""
        analyzer = CircularImportAnalyzer()
        
        analyzer._detect_circular_imports()
        assert analyzer._circular_imports == []
        
        infos = analyzer.measure_circular_import_impact()
        assert infos == []

    def test_large_cycle_detection(self):
        """Test detection of large circular dependencies."""
        analyzer = CircularImportAnalyzer()
        
        # Create a large cycle: a -> b -> c -> ... -> j -> a
        modules = [f'module_{chr(97+i)}' for i in range(10)]
        graph = {}
        for i in range(len(modules)):
            next_module = modules[(i + 1) % len(modules)]
            graph[modules[i]] = {next_module}
        
        analyzer._import_graph = graph
        analyzer._detect_circular_imports()
        
        assert len(analyzer._circular_imports) >= 1
        cycle = analyzer._circular_imports[0]
        assert len(cycle) == 11  # 10 modules + repeated first