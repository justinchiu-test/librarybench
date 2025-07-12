"""Tests for the memory analyzer module."""

from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from import_performance_optimizer.memory_analyzer import MemoryAnalyzer
from import_performance_optimizer.models import MemoryFootprint


class TestMemoryAnalyzer:
    """Test suite for MemoryAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test memory analyzer initializes correctly."""
        analyzer = MemoryAnalyzer()
        assert analyzer._baseline_memory is None
        assert analyzer._module_memory == {}
        assert len(analyzer._import_tree) == 0

    @patch('psutil.Process')
    def test_start_analysis(self, mock_process):
        """Test starting memory analysis."""
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_process.return_value.memory_info.return_value = mock_memory_info
        
        analyzer = MemoryAnalyzer()
        analyzer.start_analysis()
        
        assert analyzer._baseline_memory == 100 * 1024 * 1024
        assert analyzer._module_memory == {}

    def test_measure_module_memory(self):
        """Test measuring memory footprint of a module."""
        analyzer = MemoryAnalyzer()
        
        # Mock the memory measurement directly
        analyzer._get_current_memory = MagicMock(side_effect=[
            100 * 1024 * 1024,  # Before import: 100MB
            110 * 1024 * 1024   # After import: 110MB
        ])
        
        # Ensure test_module is not in sys.modules
        import sys
        test_module_name = 'test_memory_module_xyz'
        if test_module_name in sys.modules:
            del sys.modules[test_module_name]
        
        # Clear cache
        analyzer._module_memory.clear()
        
        # Mock importlib to not actually import
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            
            # Add to sys.modules after import
            def import_side_effect(name):
                sys.modules[name] = mock_module
                return mock_module
            
            mock_import.side_effect = import_side_effect
            
            memory_used = analyzer.measure_module_memory(test_module_name)
        
        assert memory_used == 10 * 1024 * 1024  # 10MB
        assert analyzer._module_memory[test_module_name] == 10 * 1024 * 1024
        
        # Clean up
        if test_module_name in sys.modules:
            del sys.modules[test_module_name]

    def test_get_memory_footprints(self):
        """Test getting memory footprint information."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'module_a': 5 * 1024 * 1024,  # 5MB
            'module_b': 3 * 1024 * 1024,  # 3MB
            'module_c': 2 * 1024 * 1024   # 2MB
        }
        analyzer._import_tree = {
            'module_a': ['module_b'],
            'module_b': ['module_c']
        }
        
        footprints = analyzer.get_memory_footprints()
        
        assert len(footprints) == 3
        assert all(isinstance(f, MemoryFootprint) for f in footprints)
        assert footprints[0].cumulative_memory >= footprints[0].direct_memory

    def test_calculate_cumulative_memory(self):
        """Test cumulative memory calculation."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'parent': 5 * 1024 * 1024,
            'child1': 3 * 1024 * 1024,
            'child2': 2 * 1024 * 1024
        }
        analyzer._import_tree = {
            'parent': ['child1', 'child2']
        }
        
        cumulative = analyzer._calculate_cumulative_memory()
        
        assert cumulative['parent'] == 10 * 1024 * 1024  # 5 + 3 + 2
        assert cumulative['child1'] == 3 * 1024 * 1024
        assert cumulative['child2'] == 2 * 1024 * 1024

    def test_identify_memory_heavy_branches(self):
        """Test identifying memory-heavy dependency branches."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'heavy_module': 15 * 1024 * 1024,  # 15MB
            'medium_module': 8 * 1024 * 1024,  # 8MB
            'light_module': 1 * 1024 * 1024    # 1MB
        }
        
        heavy_branches = analyzer.identify_memory_heavy_branches(threshold_mb=10.0)
        
        assert len(heavy_branches) == 1
        assert heavy_branches[0][0] == 'heavy_module'
        assert heavy_branches[0][1] == 15 * 1024 * 1024

    def test_memory_tree_visualization(self):
        """Test memory usage tree visualization."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'root': 5 * 1024 * 1024,
            'child': 2 * 1024 * 1024
        }
        analyzer._import_tree = {
            'root': ['child']
        }
        
        visualization = analyzer.get_memory_tree_visualization()
        
        assert 'root' in visualization
        assert 'child' in visualization
        assert 'MB' in visualization

    def test_get_optimization_opportunities(self):
        """Test identifying memory optimization opportunities."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'large_module': 10 * 1024 * 1024,  # 10MB
            'duplicate_1': 3 * 1024 * 1024,    # 3MB
            'duplicate_2': 3 * 1024 * 1024     # 3MB
        }
        analyzer._import_tree = {
            'parent1': ['duplicate_1'],
            'parent2': ['duplicate_1']
        }
        
        opportunities = analyzer.get_optimization_opportunities()
        
        assert len(opportunities['large_modules']) >= 1
        assert opportunities['total_potential_savings'] > 0

    def test_circular_dependency_handling(self):
        """Test handling of circular dependencies in memory calculation."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'module_a': 5 * 1024 * 1024,
            'module_b': 3 * 1024 * 1024
        }
        analyzer._import_tree = {
            'module_a': ['module_b'],
            'module_b': ['module_a']
        }
        
        cumulative = analyzer._calculate_cumulative_memory()
        
        # Should handle circular deps without infinite recursion
        assert 'module_a' in cumulative
        assert 'module_b' in cumulative

    def test_format_bytes(self):
        """Test human-readable byte formatting."""
        analyzer = MemoryAnalyzer()
        visualization = analyzer.get_memory_tree_visualization()
        
        # Test various sizes
        analyzer._module_memory = {
            'bytes': 500,
            'kilobytes': 5 * 1024,
            'megabytes': 5 * 1024 * 1024,
            'gigabytes': 5 * 1024 * 1024 * 1024
        }
        
        visualization = analyzer.get_memory_tree_visualization()
        
        assert 'B' in visualization or 'KB' in visualization or 'MB' in visualization

    def test_import_error_handling(self):
        """Test handling of import errors."""
        analyzer = MemoryAnalyzer()
        
        # Should return 0 for modules that can't be imported
        memory = analyzer.measure_module_memory('non_existent_module_xyz')
        assert memory == 0

    def test_memory_measurement_accuracy(self):
        """Test memory measurement accuracy requirements."""
        analyzer = MemoryAnalyzer()
        analyzer._module_memory = {
            'numpy': 50 * 1024 * 1024,      # 50MB
            'pandas': 100 * 1024 * 1024,    # 100MB
            'scipy': 75 * 1024 * 1024       # 75MB
        }
        
        footprints = analyzer.get_memory_footprints()
        
        # Verify percentage calculations
        total = sum(f.direct_memory for f in footprints)
        for footprint in footprints:
            expected_percentage = (footprint.cumulative_memory / total * 100)
            assert abs(footprint.percentage_of_total - expected_percentage) < 0.1

    def test_performance_requirements(self):
        """Test analyzer meets performance requirements."""
        import time
        
        analyzer = MemoryAnalyzer()
        
        # Simulate analyzing 10,000 imports
        start_time = time.perf_counter()
        
        for i in range(10000):
            analyzer._module_memory[f'module_{i}'] = i * 1024
            if i % 10 == 0 and i > 0:
                analyzer._import_tree[f'module_{i-10}'] = [f'module_{i}']
        
        analyzer.get_memory_footprints()
        
        elapsed = time.perf_counter() - start_time
        
        # Should complete analysis in under 30 seconds
        assert elapsed < 30.0

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        analyzer = MemoryAnalyzer()
        
        # Test empty analysis
        footprints = analyzer.get_memory_footprints()
        assert footprints == []
        
        # Test with no imports
        opportunities = analyzer.get_optimization_opportunities()
        assert opportunities['total_potential_savings'] == 0
        
        # Test negative memory (shouldn't happen but handle gracefully)
        analyzer._module_memory = {'test': -1000}
        footprints = analyzer.get_memory_footprints()
        assert len(footprints) == 1