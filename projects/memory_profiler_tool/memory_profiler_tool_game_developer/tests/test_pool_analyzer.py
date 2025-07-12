"""Tests for the object pool analyzer module."""

import time
import pytest
from pymemtrace.pool_analyzer import (
    ObjectPoolAnalyzer, ObjectPool, PoolMetrics, AllocationPattern
)


class GameObject:
    """Simple game object for testing."""
    def __init__(self):
        self.data = [0] * 100
        self.active = True
    
    def reset(self):
        """Reset object state."""
        self.data = [0] * 100
        self.active = True


class TestObjectPool:
    """Test suite for ObjectPool."""
    
    def test_pool_initialization(self):
        """Test pool initialization."""
        pool = ObjectPool(GameObject, initial_size=5, max_size=10, name="GameObjectPool")
        
        assert pool.name == "GameObjectPool"
        assert pool.initial_size == 5
        assert pool.max_size == 10
        assert len(pool._pool) == 5
    
    def test_acquire_release(self):
        """Test acquiring and releasing objects."""
        pool = ObjectPool(GameObject, initial_size=2, max_size=5)
        
        # Acquire from pre-populated pool
        obj1 = pool.acquire()
        assert isinstance(obj1, GameObject)
        assert pool.allocation_savings == 1
        
        # Acquire another
        obj2 = pool.acquire()
        assert pool.allocation_savings == 2
        
        # Pool should be empty now, next acquire creates new
        obj3 = pool.acquire()
        assert pool.total_allocations == 1
        
        # Release objects back
        pool.release(obj1)
        pool.release(obj2)
        
        assert len(pool._pool) == 2
    
    def test_pool_overflow(self):
        """Test pool overflow handling."""
        pool = ObjectPool(GameObject, initial_size=0, max_size=2)
        
        objects = []
        # Acquire more than max_size
        for _ in range(3):
            objects.append(pool.acquire())
        
        assert pool.overflow_count == 1
        assert pool.total_allocations == 3
    
    def test_metrics_collection(self):
        """Test pool metrics."""
        pool = ObjectPool(GameObject, initial_size=5, max_size=10)
        
        # Perform some operations
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        pool.release(obj1)
        
        metrics = pool.get_metrics()
        
        assert metrics.pool_name == "GameObject"
        assert metrics.pool_size == 4  # 5 initial - 2 acquired + 1 released
        assert metrics.active_objects == 1
        assert metrics.total_allocations == 0
        assert metrics.allocation_savings == 2
        assert metrics.utilization_rate == 0.1  # 1/10


class TestObjectPoolAnalyzer:
    """Test suite for ObjectPoolAnalyzer."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = ObjectPoolAnalyzer()
        assert len(analyzer.pools) == 0
    
    def test_create_pool(self):
        """Test pool creation through analyzer."""
        analyzer = ObjectPoolAnalyzer()
        
        pool = analyzer.create_pool(
            GameObject,
            initial_size=10,
            max_size=20,
            name="TestPool"
        )
        
        assert "TestPool" in analyzer.pools
        assert analyzer.get_pool("TestPool") == pool
    
    def test_efficiency_analysis(self):
        """Test pool efficiency analysis."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(GameObject, name="EfficiencyTest")
        
        # Simulate usage
        objects = []
        for _ in range(15):
            objects.append(pool.acquire())
        
        for obj in objects[:10]:
            pool.release(obj)
        
        efficiency = analyzer.analyze_efficiency("EfficiencyTest")
        
        assert "allocation_reduction" in efficiency
        assert "overflow_rate" in efficiency
        assert "utilization_efficiency" in efficiency
        assert "gc_impact_reduction" in efficiency
        assert efficiency["allocation_reduction"] > 0
    
    def test_allocation_pattern_recording(self):
        """Test allocation pattern recording."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(GameObject, name="PatternTest")
        
        # Create allocation pattern
        for _ in range(10):
            obj = pool.acquire()
            time.sleep(0.001)
            pool.release(obj)
        
        analyzer.record_allocation_pattern("PatternTest")
        
        patterns = analyzer._allocation_patterns["PatternTest"]
        assert len(patterns) > 0
    
    def test_pool_size_suggestion(self):
        """Test pool size optimization suggestions."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(GameObject, initial_size=5, max_size=10, name="SizeTest")
        
        # Simulate varied usage patterns
        for i in range(5):
            # Acquire varying numbers of objects
            objects = [pool.acquire() for _ in range(i + 3)]
            analyzer.record_allocation_pattern("SizeTest")
            for obj in objects:
                pool.release(obj)
            time.sleep(0.01)
        
        suggestion = analyzer.suggest_pool_size("SizeTest")
        
        assert "suggested_size" in suggestion
        assert "current_size" in suggestion
        assert suggestion["current_size"] == 10
        assert suggestion["suggested_size"] > 0
    
    def test_gc_impact_measurement(self):
        """Test garbage collection impact measurement."""
        analyzer = ObjectPoolAnalyzer()
        
        # Create multiple pools with usage
        for i in range(3):
            pool = analyzer.create_pool(GameObject, name=f"Pool{i}")
            for _ in range(10):
                obj = pool.acquire()
                pool.release(obj)
        
        gc_impact = analyzer.measure_gc_impact()
        
        assert gc_impact["total_allocations_saved"] > 0
        assert gc_impact["total_memory_saved"] > 0
        assert gc_impact["pools_analyzed"] == 3
    
    def test_pool_comparison(self):
        """Test comparison across multiple pools."""
        analyzer = ObjectPoolAnalyzer()
        
        # Create pools with different efficiency
        efficient_pool = analyzer.create_pool(GameObject, initial_size=20, name="Efficient")
        inefficient_pool = analyzer.create_pool(GameObject, initial_size=1, name="Inefficient")
        
        # Use efficient pool well
        for _ in range(15):
            obj = efficient_pool.acquire()
            efficient_pool.release(obj)
        
        # Use inefficient pool poorly
        for _ in range(15):
            obj = inefficient_pool.acquire()
            # Don't release - force new allocations
        
        comparison = analyzer.get_pool_comparison()
        
        assert len(comparison) == 2
        assert comparison[0]["pool_name"] == "Efficient"  # Should be ranked first
        assert comparison[0]["effectiveness_score"] > comparison[1]["effectiveness_score"]
    
    def test_optimize_all_pools(self):
        """Test optimization of all pools."""
        analyzer = ObjectPoolAnalyzer()
        
        # Create multiple pools
        for i in range(3):
            pool = analyzer.create_pool(GameObject, max_size=10, name=f"Pool{i}")
            # Simulate usage
            for j in range(5 + i * 2):
                pool.acquire()
        
        optimizations = analyzer.optimize_all_pools()
        
        assert len(optimizations) == 3
        for pool_name, optimization in optimizations.items():
            assert "suggested_size" in optimization
            assert optimization["suggested_size"] > 0
    
    def test_reset_metrics(self):
        """Test resetting pool metrics."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(GameObject, name="ResetTest")
        
        # Generate some metrics
        for _ in range(5):
            obj = pool.acquire()
            pool.release(obj)
        
        assert pool.total_allocations > 0 or pool.allocation_savings > 0
        
        # Reset specific pool
        analyzer.reset_metrics("ResetTest")
        assert pool.total_allocations == 0
        assert pool.allocation_savings == 0
        
        # Test reset all
        pool.acquire()  # Generate a metric
        analyzer.reset_metrics()  # Reset all
        assert pool.total_allocations == 0
    
    def test_high_allocation_rate_detection(self):
        """Test detection of high allocation rates."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(GameObject, max_size=50, name="HighRateTest")
        
        # Simulate high allocation rate over time window
        objects = []
        for _ in range(100):
            obj = pool.acquire()
            objects.append(obj)
        
        # Record pattern while objects are still allocated
        analyzer.record_allocation_pattern("HighRateTest")
        
        # Release some to allow pattern analysis
        for obj in objects[:50]:
            pool.release(obj)
            
        suggestion = analyzer.suggest_pool_size("HighRateTest")
        
        # Should suggest a reasonable size based on usage
        assert suggestion["suggested_size"] > 0
        assert "suggested_size" in suggestion
    
    def test_pool_with_no_data(self):
        """Test handling pools with no usage data."""
        analyzer = ObjectPoolAnalyzer()
        analyzer.create_pool(GameObject, name="EmptyPool")
        
        suggestion = analyzer.suggest_pool_size("EmptyPool")
        assert suggestion["reason"] == "no_data"
        assert suggestion["suggested_size"] == 10  # Default