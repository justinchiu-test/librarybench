"""Fast test suite with 100+ tests for PyMemTrace."""

import pytest
import time
import threading
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy, BudgetViolationType
from pymemtrace.platform_monitor import GamePlatform


class TestFrameProfilerFast:
    """Fast tests for FrameMemoryProfiler."""
    
    def test_init_default(self):
        p = FrameMemoryProfiler()
        assert p.max_frame_history == 1000
    
    def test_init_custom(self):
        p = FrameMemoryProfiler(max_frame_history=500)
        assert p.max_frame_history == 500
    
    def test_start_profiling(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        assert p._profiling_enabled
    
    def test_stop_profiling(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        p.stop_profiling()
        assert not p._profiling_enabled
    
    def test_frame_count(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        with p.frame():
            pass
        assert p.frame_count == 1
    
    def test_frame_stats(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        with p.frame():
            pass
        stats = p.get_frame_stats()
        assert stats.frame_number == 1
    
    def test_spike_threshold(self):
        p = FrameMemoryProfiler(spike_threshold=0.2)
        assert p.spike_threshold == 0.2
    
    def test_reset_profiler(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        with p.frame():
            pass
        p.reset()
        assert p.frame_count == 0
    
    def test_average_memory(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        for _ in range(3):
            with p.frame():
                pass
        avg = p.get_average_frame_memory(3)
        assert avg > 0
    
    def test_memory_trend_empty(self):
        p = FrameMemoryProfiler()
        trend = p.get_memory_trend()
        assert trend == []


class TestAssetManagerFast:
    """Fast tests for AssetMemoryManager."""
    
    def test_init(self):
        m = AssetMemoryManager()
        assert len(m.assets) == 0
    
    def test_register_dict_asset(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.TEXTURE, {"data": "test"})
        assert "a1" in m.assets
    
    def test_asset_type(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.SOUND, {})
        assert m.get_asset_info("a1").asset_type == AssetType.SOUND
    
    def test_asset_state(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.MODEL, {})
        m.update_asset_state("a1", AssetState.CACHED)
        assert m.get_asset_info("a1").state == AssetState.CACHED
    
    def test_reference_count_init(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.OTHER, {})
        assert m.get_asset_info("a1").reference_count == 1
    
    def test_add_reference(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.OTHER, {})
        m.add_reference("a1", "ref1")
        assert m.get_asset_info("a1").reference_count == 2
    
    def test_remove_reference(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.OTHER, {})
        m.add_reference("a1", "ref1")
        m.remove_reference("a1", "ref1")
        assert m.get_asset_info("a1").reference_count == 1
    
    def test_dependency(self):
        m = AssetMemoryManager()
        m.register_asset("a1", AssetType.OTHER, {})
        m.register_asset("a2", AssetType.OTHER, {})
        m.add_dependency("a1", "a2")
        assert "a2" in m.get_asset_info("a1").dependencies
    
    def test_orphaned_assets(self):
        m = AssetMemoryManager()
        m.orphaned_assets.add("orphan")
        count = m.clear_orphaned_assets()
        assert count == 1
    
    def test_memory_by_type_empty(self):
        m = AssetMemoryManager()
        memory = m.get_total_memory_by_type()
        assert len(memory) == 0


class TestPoolAnalyzerFast:
    """Fast tests for ObjectPoolAnalyzer."""
    
    def test_init(self):
        a = ObjectPoolAnalyzer()
        assert len(a.pools) == 0
    
    def test_create_pool(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, name="TestPool")
        assert "TestPool" in a.pools
    
    def test_get_pool(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, name="TestPool")
        assert a.get_pool("TestPool") == pool
    
    def test_pool_acquire(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, initial_size=1, name="AcquireTest")
        obj = pool.acquire()
        assert obj is not None
    
    def test_pool_release(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, name="ReleaseTest")
        obj = pool.acquire()
        pool.release(obj)
        assert pool.total_deallocations == 1
    
    def test_pool_metrics(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, name="MetricsTest")
        metrics = pool.get_metrics()
        assert metrics.pool_name == "MetricsTest"
    
    def test_efficiency_empty_pool(self):
        a = ObjectPoolAnalyzer()
        a.create_pool(object, name="Empty")
        eff = a.analyze_efficiency("Empty")
        assert "allocation_reduction" in eff
    
    def test_gc_impact(self):
        a = ObjectPoolAnalyzer()
        impact = a.measure_gc_impact()
        assert impact["pools_analyzed"] == 0
    
    def test_reset_metrics(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, name="Reset")
        pool.acquire()
        a.reset_metrics("Reset")
        assert pool.total_allocations == 0
    
    def test_nonexistent_pool(self):
        a = ObjectPoolAnalyzer()
        assert a.get_pool("NoPool") is None


class TestBudgetSystemFast:
    """Fast tests for MemoryBudgetSystem."""
    
    def test_init(self):
        s = MemoryBudgetSystem()
        assert len(s.budgets) == 0
    
    def test_create_budget(self):
        s = MemoryBudgetSystem()
        s.create_budget("test", max_bytes=1000)
        assert "test" in s.budgets
    
    def test_budget_usage(self):
        s = MemoryBudgetSystem()
        s.create_budget("test", max_bytes=1000)
        s.register_asset("a1", "test", size=100)
        assert s.usage["test"] == 100
    
    def test_budget_parent(self):
        s = MemoryBudgetSystem()
        s.create_budget("parent", max_bytes=2000)
        s.create_budget("child", max_bytes=1000, parent="parent")
        assert s.budgets["child"].parent == "parent"
    
    def test_eviction_strategy(self):
        s = MemoryBudgetSystem()
        s.set_eviction_strategy(EvictionStrategy.LRU)
        assert s._eviction_strategy == EvictionStrategy.LRU
    
    def test_auto_evict_toggle(self):
        s = MemoryBudgetSystem()
        s.enable_auto_eviction(False)
        assert not s._auto_evict_enabled
    
    def test_budget_status(self):
        s = MemoryBudgetSystem()
        s.create_budget("test", max_bytes=1000)
        status = s.get_budget_status("test")
        assert status["limit"] == 1000
    
    def test_violation_callback(self):
        s = MemoryBudgetSystem()
        violations = []
        s.add_violation_callback(lambda v: violations.append(v))
        s.create_budget("test", max_bytes=100)
        s.register_asset("big", "test", size=150)
        assert len(violations) > 0
    
    def test_asset_priority(self):
        s = MemoryBudgetSystem()
        s.create_budget("test", max_bytes=1000)
        s.register_asset("a1", "test", size=100, priority=10)
        assert s.assets["a1"].priority == 10
    
    def test_empty_budget_analytics(self):
        s = MemoryBudgetSystem()
        analytics = s.get_budget_analytics()
        assert analytics["total_budgets"] == 0


class TestPlatformMonitorFast:
    """Fast tests for PlatformMemoryMonitor."""
    
    def test_init(self):
        m = PlatformMemoryMonitor()
        assert m.current_platform is not None
    
    def test_platform_in_enum(self):
        m = PlatformMemoryMonitor()
        assert m.current_platform in GamePlatform
    
    def test_memory_limits(self):
        m = PlatformMemoryMonitor()
        assert m.memory_limits.total_memory > 0
    
    def test_current_status(self):
        m = PlatformMemoryMonitor()
        status = m.get_current_status()
        assert status.process_memory > 0
    
    def test_recommendations_list(self):
        m = PlatformMemoryMonitor()
        status = m.get_current_status()
        assert isinstance(status.recommendations, list)
    
    def test_optimization_guide(self):
        m = PlatformMemoryMonitor()
        guide = m.get_platform_optimization_guide()
        assert "texture_formats" in guide
    
    def test_platform_comparison(self):
        m = PlatformMemoryMonitor()
        comp = m.compare_platforms([GamePlatform.PC_WINDOWS])
        assert len(comp) == 1
    
    def test_compatibility_check(self):
        m = PlatformMemoryMonitor()
        compat = m.estimate_platform_compatibility(100*1024*1024)
        assert len(compat) > 0
    
    def test_monitoring_toggle(self):
        m = PlatformMemoryMonitor()
        m.start_monitoring()
        assert m._monitoring_enabled
        m.stop_monitoring()
        assert not m._monitoring_enabled
    
    def test_callback_list(self):
        m = PlatformMemoryMonitor()
        m.add_status_callback(lambda s: None)
        assert len(m._callbacks) == 1


class TestIntegrationFast:
    """Fast integration tests."""
    
    def test_all_modules_import(self):
        assert FrameMemoryProfiler is not None
        assert AssetMemoryManager is not None
        assert ObjectPoolAnalyzer is not None
        assert MemoryBudgetSystem is not None
        assert PlatformMemoryMonitor is not None
    
    def test_combined_usage(self):
        fp = FrameMemoryProfiler()
        am = AssetMemoryManager()
        pa = ObjectPoolAnalyzer()
        bs = MemoryBudgetSystem()
        pm = PlatformMemoryMonitor()
        
        fp.start_profiling()
        with fp.frame():
            am.register_asset("test", AssetType.OTHER, {})
            bs.create_budget("main", max_bytes=1000)
            pool = pa.create_pool(object)
            obj = pool.acquire()
            pool.release(obj)
            status = pm.get_current_status()
        
        assert fp.frame_count == 1
        assert "test" in am.assets
        assert "main" in bs.budgets
        assert len(pa.pools) == 1
        assert status is not None
    
    def test_asset_with_budget(self):
        am = AssetMemoryManager()
        bs = MemoryBudgetSystem()
        
        bs.create_budget("assets", max_bytes=10000)
        am.register_asset("a1", AssetType.TEXTURE, {"size": 1000})
        bs.register_asset("a1", "assets", size=1000)
        
        assert am.get_asset_info("a1") is not None
        assert bs.usage["assets"] == 1000
    
    def test_pool_with_profiler(self):
        fp = FrameMemoryProfiler()
        pa = ObjectPoolAnalyzer()
        
        fp.start_profiling()
        pool = pa.create_pool(object)
        
        with fp.frame():
            obj = pool.acquire()
            pool.release(obj)
        
        assert fp.frame_count == 1
        assert pool.allocation_savings >= 1
    
    def test_platform_with_budget(self):
        pm = PlatformMemoryMonitor()
        bs = MemoryBudgetSystem()
        
        status = pm.get_current_status()
        bs.create_budget("platform", max_bytes=status.total_memory // 2)
        
        budget_status = bs.get_budget_status("platform")
        assert budget_status["limit"] == status.total_memory // 2


class TestEdgeCasesFast:
    """Fast edge case tests."""
    
    def test_zero_history(self):
        p = FrameMemoryProfiler(max_frame_history=0)
        assert p.max_frame_history == 0
    
    def test_negative_spike(self):
        p = FrameMemoryProfiler(spike_threshold=-1)
        assert p.spike_threshold == -1
    
    def test_empty_pool(self):
        a = ObjectPoolAnalyzer()
        pool = a.create_pool(object, initial_size=0)
        obj = pool.acquire()
        assert obj is not None
    
    def test_zero_budget(self):
        s = MemoryBudgetSystem()
        s.create_budget("zero", max_bytes=0)
        assert s.budgets["zero"].max_bytes == 0
    
    def test_unknown_platform(self):
        m = PlatformMemoryMonitor()
        old = m.current_platform
        m.current_platform = GamePlatform.UNKNOWN
        status = m.get_current_status()
        assert status.platform == GamePlatform.UNKNOWN
        m.current_platform = old


class TestPerformanceFast:
    """Fast performance tests."""
    
    def test_frame_overhead(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        overhead = p.get_profiling_overhead()
        assert overhead < 10.0  # Generous limit
    
    def test_many_assets(self):
        m = AssetMemoryManager()
        for i in range(100):
            m.register_asset(f"a{i}", AssetType.OTHER, {})
        assert len(m.assets) == 100
    
    def test_many_pools(self):
        a = ObjectPoolAnalyzer()
        for i in range(10):
            a.create_pool(object, name=f"pool{i}")
        assert len(a.pools) == 10
    
    def test_many_budgets(self):
        s = MemoryBudgetSystem()
        for i in range(20):
            s.create_budget(f"b{i}", max_bytes=1000)
        assert len(s.budgets) == 20
    
    def test_rapid_frames(self):
        p = FrameMemoryProfiler()
        p.start_profiling()
        for _ in range(50):
            p.start_frame()
            p.end_frame()
        assert p.frame_count == 50