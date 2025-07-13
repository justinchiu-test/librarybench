"""Tests for fragmentation module."""

import pytest
from src.fragmentation import FragmentationAnalyzer, MemoryBlock, FragmentationMetrics


class TestFragmentationAnalyzer:
    """Test suite for FragmentationAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = FragmentationAnalyzer()
        assert analyzer.memory_size == 1024 * 1024
        assert len(analyzer.memory_blocks) == 1
        assert analyzer.memory_blocks[0].is_free
        assert analyzer.memory_blocks[0].size == analyzer.memory_size
        
    def test_allocation(self):
        """Test memory allocation."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Allocate memory
        addr1 = analyzer.allocate(100, "test_obj")
        assert addr1 is not None
        assert addr1 == 0
        
        # Check memory blocks
        assert len(analyzer.memory_blocks) == 2
        assert not analyzer.memory_blocks[0].is_free
        assert analyzer.memory_blocks[0].size == 100
        assert analyzer.memory_blocks[1].is_free
        assert analyzer.memory_blocks[1].size == 900
        
    def test_allocation_failure(self):
        """Test allocation failure when no space."""
        analyzer = FragmentationAnalyzer(memory_size=100)
        
        # Allocate all memory
        addr = analyzer.allocate(100, "full")
        assert addr is not None
        
        # Try to allocate more
        addr2 = analyzer.allocate(50, "fail")
        assert addr2 is None
        
    def test_free_memory(self):
        """Test freeing memory."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Allocate and free
        addr = analyzer.allocate(100, "test")
        assert addr is not None
        
        success = analyzer.free(addr)
        assert success
        
        # Should have one free block again
        assert len(analyzer.memory_blocks) == 1
        assert analyzer.memory_blocks[0].is_free
        assert analyzer.memory_blocks[0].size == 1000
        
    def test_fragmentation_creation(self):
        """Test creation of fragmentation."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Create fragmentation pattern
        addr1 = analyzer.allocate(100, "obj1")
        addr2 = analyzer.allocate(100, "obj2")
        addr3 = analyzer.allocate(100, "obj3")
        
        # Free middle block
        analyzer.free(addr2)
        
        # Should have fragmentation
        assert len(analyzer.memory_blocks) == 4
        free_blocks = [b for b in analyzer.memory_blocks if b.is_free]
        assert len(free_blocks) == 2
        
    def test_coalescing(self):
        """Test coalescing of adjacent free blocks."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Create adjacent allocations
        addr1 = analyzer.allocate(100, "obj1")
        addr2 = analyzer.allocate(100, "obj2")
        addr3 = analyzer.allocate(100, "obj3")
        
        # Free adjacent blocks
        analyzer.free(addr1)
        analyzer.free(addr2)
        
        # Should coalesce into one free block
        free_blocks = [b for b in analyzer.memory_blocks if b.is_free]
        assert len(free_blocks) == 2  # One at start, one at end
        assert free_blocks[0].size == 200  # Coalesced size
        
    def test_metrics_calculation(self):
        """Test fragmentation metrics calculation."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        # Create fragmentation
        addr1 = analyzer.allocate(200, "obj1")
        addr2 = analyzer.allocate(200, "obj2")
        addr3 = analyzer.allocate(200, "obj3")
        analyzer.free(addr2)
        
        metrics = analyzer.calculate_metrics()
        
        assert metrics.total_memory == 1000
        assert metrics.used_memory == 400
        assert metrics.free_memory == 600
        assert metrics.free_block_count == 2
        assert metrics.largest_free_block == 400
        assert metrics.fragmentation_percentage > 0
        assert 0 <= metrics.memory_efficiency <= 1
        
    def test_memory_visualization(self):
        """Test memory visualization."""
        analyzer = FragmentationAnalyzer(memory_size=100)
        
        # Create pattern
        analyzer.allocate(25, "obj1")
        analyzer.allocate(25, "obj2")
        analyzer.allocate(25, "obj3")
        
        viz = analyzer.visualize_memory(width=40)
        
        assert isinstance(viz, str)
        assert "Memory Map" in viz
        assert "█" in viz  # Used blocks
        assert "Legend" in viz
        
    def test_fragmentation_hotspots(self):
        """Test identification of fragmentation hotspots."""
        analyzer = FragmentationAnalyzer()
        
        # Create varied allocation pattern
        for i in range(10):
            analyzer.allocate(100 + i * 50, f"type_a")
            
        for i in range(10):
            analyzer.allocate(50, f"type_b")
            
        hotspots = analyzer.identify_fragmentation_hotspots()
        
        assert isinstance(hotspots, list)
        # Type with varying sizes should have higher fragmentation score
        if hotspots:
            assert hotspots[0][1] > 0  # Fragmentation score
            
    def test_defragmentation_suggestions(self):
        """Test defragmentation suggestions."""
        analyzer = FragmentationAnalyzer(memory_size=10000)
        
        # Create high fragmentation
        addrs = []
        for i in range(50):
            addr = analyzer.allocate(100, f"obj_{i}")
            addrs.append(addr)
            
        # Free every other allocation
        for i in range(0, 50, 2):
            analyzer.free(addrs[i])
            
        suggestions = analyzer.suggest_defragmentation_strategies()
        
        assert len(suggestions) > 0
        assert any("fragmentation" in s.lower() for s in suggestions)
        
    def test_analyze_allocation_pattern(self):
        """Test analyzing allocation patterns."""
        analyzer = FragmentationAnalyzer(memory_size=10000)
        
        allocations = [
            (100, "small"),
            (1000, "large"),
            (50, "tiny"),
            (500, "medium"),
            (100, "small"),
            (2000, "huge"),
        ]
        
        report = analyzer.analyze_allocation_pattern(allocations)
        
        assert report.metrics.total_memory == 10000
        assert len(report.memory_map) > 0
        assert isinstance(report.visualization, str)
        
    def test_export_memory_map(self):
        """Test exporting memory map."""
        analyzer = FragmentationAnalyzer(memory_size=1000)
        
        analyzer.allocate(100, "obj1")
        analyzer.allocate(200, "obj2")
        
        memory_map = analyzer.export_memory_map()
        
        assert isinstance(memory_map, list)
        assert len(memory_map) == 3  # 2 allocated + 1 free
        
        for block in memory_map:
            assert 'address' in block
            assert 'size' in block
            assert 'is_free' in block
            assert 'end_address' in block
            
    def test_memory_block_properties(self):
        """Test MemoryBlock properties."""
        block = MemoryBlock(address=100, size=50, is_free=False, object_type="test")
        
        assert block.address == 100
        assert block.size == 50
        assert not block.is_free
        assert block.object_type == "test"
        assert block.end_address == 150
        
    def test_edge_cases(self):
        """Test edge cases."""
        analyzer = FragmentationAnalyzer(memory_size=100)
        
        # Allocate exact size
        addr = analyzer.allocate(100, "exact")
        assert addr == 0
        assert len(analyzer.memory_blocks) == 1
        
        # Free non-existent address
        success = analyzer.free(1000)
        assert not success
        
        # Zero allocation
        addr = analyzer.allocate(0, "zero")
        assert addr is not None