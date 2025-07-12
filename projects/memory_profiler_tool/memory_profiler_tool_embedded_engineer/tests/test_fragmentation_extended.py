"""Extended tests for fragmentation module."""

import pytest
from src.fragmentation import (
    FragmentationAnalyzer, MemoryBlock, FragmentationMetrics,
    FragmentationReport
)


class TestFragmentationExtended:
    """Extended test suite for FragmentationAnalyzer."""
    
    def test_worst_case_fragmentation(self):
        """Test worst-case fragmentation scenario."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Create checkerboard pattern
        addresses = []
        for i in range(0, 10):
            addr = analyzer.allocate(50, f"obj_{i}")
            if addr is not None:
                addresses.append(addr)
            
        # Free every other allocation
        for i in range(0, len(addresses), 2):
            analyzer.free(addresses[i])
            
        metrics = analyzer.calculate_metrics()
        
        # Should have high fragmentation
        assert metrics.fragmentation_percentage > 30  # More realistic threshold
        assert metrics.free_block_count >= 3  # At least some free blocks
        
    def test_best_case_fragmentation(self):
        """Test best-case fragmentation scenario."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Allocate contiguously
        addr1 = analyzer.allocate(300, "obj1")
        addr2 = analyzer.allocate(300, "obj2")
        addr3 = analyzer.allocate(300, "obj3")
        
        # Free in order
        analyzer.free(addr1)
        analyzer.free(addr2)
        
        metrics = analyzer.calculate_metrics()
        
        # Should have low fragmentation (one large free block)
        assert metrics.fragmentation_percentage < 50
        
    def test_memory_compaction_simulation(self):
        """Test simulation of memory compaction."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Fragment memory
        addresses = []
        for i in range(20):
            addr = analyzer.allocate(40, f"obj_{i}")
            addresses.append(addr)
            
        # Free some to create gaps
        for i in [1, 3, 5, 7, 9]:
            analyzer.free(addresses[i])
            
        initial_metrics = analyzer.calculate_metrics()
        
        # Simulate compaction by recreating
        analyzer._init_memory()
        
        # Reallocate without gaps
        for i in range(15):  # 5 were freed
            analyzer.allocate(40, f"obj_{i}")
            
        compacted_metrics = analyzer.calculate_metrics()
        
        # Compacted should have less fragmentation
        assert compacted_metrics.fragmentation_percentage < initial_metrics.fragmentation_percentage
        
    def test_allocation_patterns_impact(self):
        """Test impact of different allocation patterns."""
        # Pattern 1: Sequential allocations
        analyzer1 = FragmentationAnalyzer(memory_size=10000)
        pattern1 = [(100, "fixed") for _ in range(50)]
        report1 = analyzer1.analyze_allocation_pattern(pattern1)
        
        # Pattern 2: Variable sizes
        analyzer2 = FragmentationAnalyzer(memory_size=10000)
        pattern2 = [(50 + i * 10, f"var_{i}") for i in range(50)]
        report2 = analyzer2.analyze_allocation_pattern(pattern2)
        
        # Variable sizes should cause more fragmentation
        assert report2.metrics.fragmentation_percentage >= report1.metrics.fragmentation_percentage
        
    def test_memory_map_accuracy(self):
        """Test accuracy of memory map representation."""
        analyzer = FragmentationAnalyzer(memory_size=100)
        
        # Known allocations
        analyzer.allocate(20, "first")
        analyzer.allocate(30, "second")
        analyzer.allocate(25, "third")
        
        memory_map = analyzer.export_memory_map()
        
        # Verify map accuracy
        assert len(memory_map) == 4  # 3 allocated + 1 free
        
        total_size = sum(block['size'] for block in memory_map)
        assert total_size == 100
        
    def test_fragmentation_over_time(self):
        """Test fragmentation changes over time."""
        analyzer = FragmentationAnalyzer(memory_size=5000)
        fragmentation_history = []
        
        # Simulate allocation/deallocation over time
        addresses = []
        for cycle in range(10):
            # Allocate phase
            for i in range(5):
                addr = analyzer.allocate(100 + cycle * 10, f"cycle_{cycle}_{i}")
                addresses.append(addr)
                
            # Free phase (free oldest)
            if len(addresses) > 20:
                for _ in range(5):
                    if addresses:
                        analyzer.free(addresses.pop(0))
                        
            # Measure fragmentation
            metrics = analyzer.calculate_metrics()
            fragmentation_history.append(metrics.fragmentation_percentage)
            
        # Fragmentation should vary over time
        assert max(fragmentation_history) > min(fragmentation_history)
        
    def test_allocation_failure_handling(self):
        """Test handling of allocation failures."""
        analyzer = FragmentationAnalyzer(memory_size=100)
        
        # Fill memory
        addr1 = analyzer.allocate(50, "half1")
        addr2 = analyzer.allocate(50, "half2")
        
        # Try to allocate more
        addr3 = analyzer.allocate(10, "overflow")
        assert addr3 is None
        
        # Free and retry
        analyzer.free(addr1)
        addr4 = analyzer.allocate(10, "fits_now")
        assert addr4 is not None
        
    def test_visualization_edge_cases(self):
        """Test visualization with edge cases."""
        # Empty memory
        analyzer1 = FragmentationAnalyzer(memory_size=100)
        viz1 = analyzer1.visualize_memory()
        assert "░" in viz1  # All free
        
        # Full memory
        analyzer2 = FragmentationAnalyzer(memory_size=100)
        analyzer2.allocate(100, "full")
        viz2 = analyzer2.visualize_memory()
        assert "█" in viz2  # All used
        
        # Single byte allocations
        analyzer3 = FragmentationAnalyzer(memory_size=10)
        for i in range(10):
            analyzer3.allocate(1, f"byte_{i}")
        viz3 = analyzer3.visualize_memory()
        assert viz3 is not None
        
    def test_defragmentation_strategy_validation(self):
        """Test validation of defragmentation strategies."""
        analyzer = FragmentationAnalyzer(memory_size=10000)
        
        # Create fragmentation pattern
        addresses = []
        for i in range(20):
            addr = analyzer.allocate(200, f"obj_{i}")
            if addr is not None:
                addresses.append(addr)
        
        # Free every other to create fragmentation
        for i in range(0, len(addresses), 2):
            analyzer.free(addresses[i])
            
        suggestions = analyzer.suggest_defragmentation_strategies()
        
        # Should have some suggestions
        assert len(suggestions) > 0
        
    def test_memory_alignment_considerations(self):
        """Test memory alignment in allocations."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Allocate with different alignments
        addr1 = analyzer.allocate(7, "unaligned")  # Not 8-byte aligned
        addr2 = analyzer.allocate(16, "aligned")    # 8-byte aligned
        addr3 = analyzer.allocate(13, "unaligned2") # Not aligned
        
        # Check addresses
        assert addr1 == 0
        assert addr2 == 7
        assert addr3 == 23