"""Edge case tests for PyMemTrace."""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy, BudgetViolationType
from pymemtrace.platform_monitor import GamePlatform


class TestFrameProfilerEdgeCases:
    """Edge case tests for FrameMemoryProfiler."""
    
    def test_zero_frame_history(self):
        """Test profiler with zero frame history."""
        profiler = FrameMemoryProfiler(max_frame_history=0)
        profiler.start_profiling()
        
        with profiler.frame():
            pass
        
        assert len(profiler.frame_history) == 0
        assert profiler.frame_count == 1
    
    def test_negative_spike_threshold(self):
        """Test profiler with negative spike threshold."""
        profiler = FrameMemoryProfiler(spike_threshold=-0.1)
        assert profiler.spike_threshold == -0.1  # Should accept it
    
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop profiling cycles."""
        profiler = FrameMemoryProfiler()
        
        for i in range(3):
            profiler.start_profiling()
            with profiler.frame():
                pass
            profiler.stop_profiling()
        
        profiler.start_profiling()
        assert profiler.frame_count == 0  # Should reset on start
    
    def test_frame_without_start(self):
        """Test profiling frame without starting profiler."""
        profiler = FrameMemoryProfiler()
        
        with profiler.frame():
            pass
        
        assert profiler.frame_count == 0
        assert len(profiler.frame_history) == 0
    
    def test_concurrent_frame_access(self):
        """Test concurrent access to frame data."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        def profile_frames():
            for _ in range(10):
                with profiler.frame():
                    time.sleep(0.001)
        
        threads = [threading.Thread(target=profile_frames) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert profiler.frame_count == 50
    
    def test_empty_frame_history_operations(self):
        """Test operations on empty frame history."""
        profiler = FrameMemoryProfiler()
        
        assert profiler.get_frame_stats() is None
        assert profiler.get_average_frame_memory() == 0.0
        assert profiler.get_memory_trend() == []
        assert profiler.detect_frame_drops() == []
    
    def test_extreme_frame_counts(self):
        """Test with extreme number of frames."""
        profiler = FrameMemoryProfiler(max_frame_history=10)
        profiler.start_profiling()
        
        for i in range(1000):
            profiler.start_frame()
            profiler.end_frame()
        
        assert len(profiler.frame_history) == 10
        assert profiler.frame_count == 1000


class TestAssetManagerEdgeCases:
    """Edge case tests for AssetMemoryManager."""
    
    def test_duplicate_asset_registration(self):
        """Test registering the same asset ID twice."""
        manager = AssetMemoryManager()
        asset1 = {"data": "first"}
        asset2 = {"data": "second"}
        
        manager.register_asset("duplicate", AssetType.TEXTURE, asset1)
        manager.register_asset("duplicate", AssetType.TEXTURE, asset2)
        
        # Should overwrite
        assert manager.get_asset_info("duplicate") is not None
    
    def test_invalid_asset_operations(self):
        """Test operations on non-existent assets."""
        manager = AssetMemoryManager()
        
        # Should handle gracefully
        manager.update_asset_state("nonexistent", AssetState.LOADED)
        manager.add_reference("nonexistent", "ref1")
        manager.remove_reference("nonexistent", "ref1")
        
        assert manager.get_asset_info("nonexistent") is None
    
    def test_negative_reference_count(self):
        """Test reference count going negative."""
        manager = AssetMemoryManager()
        manager.register_asset("asset", AssetType.MODEL, {})
        
        # Remove more references than added
        for _ in range(5):
            manager.remove_reference("asset", "ref")
        
        assert manager.get_asset_info("asset").reference_count == 0
    
    def test_self_dependency(self):
        """Test asset depending on itself."""
        manager = AssetMemoryManager()
        manager.register_asset("self_dep", AssetType.OTHER, {})
        manager.add_dependency("self_dep", "self_dep")
        
        leaks = manager.detect_memory_leaks()
        assert "self_dep" in leaks
    
    def test_massive_asset_registration(self):
        """Test registering many assets."""
        manager = AssetMemoryManager()
        
        for i in range(100):
            manager.register_asset(f"asset_{i}", AssetType.OTHER, {"id": i})
        
        assert len(manager.assets) == 100
        memory_by_type = manager.get_total_memory_by_type()
        assert AssetType.OTHER in memory_by_type
    
    def test_empty_dependency_graph(self):
        """Test dependency graph for asset with no dependencies."""
        manager = AssetMemoryManager()
        manager.register_asset("isolated", AssetType.TEXTURE, {})
        
        graph = manager.get_dependency_graph("isolated")
        assert "isolated" in graph
        assert len(graph["isolated"]) == 0
    
    def test_heatmap_with_no_loaded_assets(self):
        """Test heatmap when no assets are loaded."""
        manager = AssetMemoryManager()
        manager.register_asset("unloaded", AssetType.MODEL, {})
        manager.update_asset_state("unloaded", AssetState.UNLOADED)
        
        heatmap = manager.get_memory_heatmap()
        assert heatmap.total_memory == 0
        assert len(heatmap.hotspots) == 0


class TestPoolAnalyzerEdgeCases:
    """Edge case tests for ObjectPoolAnalyzer."""
    
    def test_zero_size_pool(self):
        """Test pool with zero initial size."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(object, initial_size=0, max_size=10)
        
        obj = pool.acquire()
        assert obj is not None
        assert pool.total_allocations == 1
    
    def test_pool_with_max_size_one(self):
        """Test pool with max size of 1."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(object, initial_size=0, max_size=1)
        
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        
        assert pool.overflow_count == 1
    
    def test_nonexistent_pool_operations(self):
        """Test operations on non-existent pool."""
        analyzer = ObjectPoolAnalyzer()
        
        efficiency = analyzer.analyze_efficiency("nonexistent")
        assert efficiency == {}
        
        analyzer.record_allocation_pattern("nonexistent")  # Should not crash
        
        suggestion = analyzer.suggest_pool_size("nonexistent")
        assert suggestion["reason"] == "no_data"
    
    def test_pool_with_failing_object_creation(self):
        """Test pool with objects that fail to create."""
        class FailingObject:
            _count = 0
            def __init__(self):
                FailingObject._count += 1
                if FailingObject._count % 3 == 0:
                    raise ValueError("Creation failed")
        
        analyzer = ObjectPoolAnalyzer()
        try:
            pool = analyzer.create_pool(FailingObject, initial_size=5)
        except ValueError:
            pass  # Expected some failures
    
    def test_extreme_allocation_rates(self):
        """Test pool with extreme allocation rates."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(object, max_size=1000)
        
        # Rapid allocations
        objects = []
        for _ in range(500):
            objects.append(pool.acquire())
        
        analyzer.record_allocation_pattern(pool.name)
        suggestion = analyzer.suggest_pool_size(pool.name)
        
        assert suggestion["suggested_size"] > 0
    
    def test_reset_nonexistent_pool(self):
        """Test resetting metrics for non-existent pool."""
        analyzer = ObjectPoolAnalyzer()
        analyzer.reset_metrics("nonexistent")  # Should not crash
    
    def test_gc_impact_with_no_pools(self):
        """Test GC impact measurement with no pools."""
        analyzer = ObjectPoolAnalyzer()
        impact = analyzer.measure_gc_impact()
        
        assert impact["total_allocations_saved"] == 0
        assert impact["pools_analyzed"] == 0


class TestBudgetSystemEdgeCases:
    """Edge case tests for MemoryBudgetSystem."""
    
    def test_zero_byte_budget(self):
        """Test budget with zero bytes."""
        system = MemoryBudgetSystem()
        system.create_budget("zero", max_bytes=0)
        
        # Any asset should exceed
        system.register_asset("any", "zero", size=1)
        assert system.usage["zero"] == 1
    
    def test_circular_budget_hierarchy(self):
        """Test circular parent-child relationships."""
        system = MemoryBudgetSystem()
        system.create_budget("a", max_bytes=1000)
        system.create_budget("b", max_bytes=1000, parent="a")
        
        # Can't create circular reference in current implementation
        # But test the hierarchy still works
        assert system.budgets["b"].parent == "a"
    
    def test_asset_larger_than_budget(self):
        """Test registering asset larger than entire budget."""
        system = MemoryBudgetSystem()
        system.create_budget("small", max_bytes=100)
        
        violations = []
        system.add_violation_callback(lambda v: violations.append(v))
        
        system.register_asset("huge", "small", size=1000)
        
        assert len(violations) > 0
        assert violations[-1].violation_type == BudgetViolationType.EXCEEDED
    
    def test_eviction_with_empty_budget(self):
        """Test eviction when no assets in budget."""
        system = MemoryBudgetSystem()
        system.create_budget("empty", max_bytes=1000)
        
        evicted = system._auto_evict("empty")
        assert evicted == []
    
    def test_all_eviction_strategies(self):
        """Test all eviction strategies."""
        strategies = [
            EvictionStrategy.LRU,
            EvictionStrategy.LFU,
            EvictionStrategy.PRIORITY,
            EvictionStrategy.SIZE,
            EvictionStrategy.AGE,
            EvictionStrategy.HYBRID
        ]
        
        for strategy in strategies:
            system = MemoryBudgetSystem()
            system.set_eviction_strategy(strategy)
            system.create_budget("test", max_bytes=1000)
            
            # Add some assets
            for i in range(3):
                system.register_asset(f"asset_{i}", "test", size=400, priority=i)
                time.sleep(0.001)
            
            # Trigger eviction
            system.register_asset("overflow", "test", size=400)
            
            assert system.usage["test"] <= 1000
    
    def test_budget_with_100_percent_thresholds(self):
        """Test budget with 100% warning and critical thresholds."""
        system = MemoryBudgetSystem()
        system.create_budget("lenient", max_bytes=1000, 
                           warning_threshold=1.0, 
                           critical_threshold=1.0)
        
        violations = []
        system.add_violation_callback(lambda v: violations.append(v))
        
        system.register_asset("fill", "lenient", size=999)
        assert len(violations) == 0  # No warnings yet
        
        system.register_asset("overflow", "lenient", size=2)
        assert len(violations) > 0  # Now exceeded
    
    def test_multiple_callbacks(self):
        """Test multiple violation and eviction callbacks."""
        system = MemoryBudgetSystem()
        
        violations = []
        evictions = []
        
        for i in range(3):
            system.add_violation_callback(lambda v, i=i: violations.append((i, v)))
            system.add_eviction_callback(lambda a, r, i=i: evictions.append((i, a, r)))
        
        system.create_budget("test", max_bytes=100)
        system.register_asset("big", "test", size=150)
        
        # All callbacks should be called
        assert len(violations) >= 3


class TestPlatformMonitorEdgeCases:
    """Edge case tests for PlatformMemoryMonitor."""
    
    def test_unknown_platform_handling(self):
        """Test handling of unknown platform."""
        monitor = PlatformMemoryMonitor()
        monitor.current_platform = GamePlatform.UNKNOWN
        monitor.memory_limits = monitor._get_platform_limits()
        
        status = monitor.get_current_status()
        assert status.platform == GamePlatform.UNKNOWN
    
    def test_extreme_memory_usage(self):
        """Test with extreme memory usage values."""
        monitor = PlatformMemoryMonitor()
        
        # Test with very high memory
        recs = monitor._generate_recommendations(
            process_memory=100 * 1024 * 1024 * 1024,  # 100GB
            available_memory=1024,  # 1KB
            memory_percentage=99.9
        )
        
        assert len(recs) > 0
        assert any("critically low" in r for r in recs)
    
    def test_all_platform_configs(self):
        """Test all platform configurations exist."""
        monitor = PlatformMemoryMonitor()
        
        for platform in GamePlatform:
            if platform != GamePlatform.UNKNOWN:
                config = monitor.PLATFORM_CONFIGS.get(platform, {})
                if config:  # Some platforms might not have config
                    assert "min_memory" in config
                    assert "recommended" in config
    
    def test_monitoring_thread_safety(self):
        """Test thread safety of monitoring."""
        monitor = PlatformMemoryMonitor()
        
        statuses = []
        
        def check_status():
            for _ in range(10):
                status = monitor.get_current_status()
                statuses.append(status)
                time.sleep(0.001)
        
        monitor.start_monitoring(interval=0.01)
        
        threads = [threading.Thread(target=check_status) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        monitor.stop_monitoring()
        assert len(statuses) == 30
    
    def test_platform_switching(self):
        """Test switching between platforms."""
        monitor = PlatformMemoryMonitor()
        
        original = monitor.current_platform
        
        # Test each platform
        for platform in [GamePlatform.MOBILE_IOS, GamePlatform.CONSOLE_XBOX, GamePlatform.WEB]:
            monitor.current_platform = platform
            monitor.memory_limits = monitor._get_platform_limits()
            
            guide = monitor.get_platform_optimization_guide()
            assert guide["platform"] == platform.value
        
        monitor.current_platform = original
    
    def test_empty_callbacks_list(self):
        """Test with no callbacks registered."""
        monitor = PlatformMemoryMonitor()
        
        # Create critical status
        status = monitor.get_current_status()
        status.is_critical = True
        
        # Should not crash with no callbacks
        for callback in monitor._callbacks:
            callback(status)
    
    def test_memory_bank_calculations(self):
        """Test memory bank calculations for consoles."""
        monitor = PlatformMemoryMonitor()
        
        # Test PlayStation banks
        monitor.current_platform = GamePlatform.CONSOLE_PLAYSTATION
        monitor.memory_limits = monitor._get_platform_limits()
        banks = monitor.get_memory_bank_usage()
        
        if banks:
            total = sum(banks.values())
            process_memory = monitor._process.memory_info().rss
            assert total == process_memory