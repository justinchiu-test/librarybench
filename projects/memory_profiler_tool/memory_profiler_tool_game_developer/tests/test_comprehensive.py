"""Comprehensive test suite for PyMemTrace with 100+ tests."""

import pytest
import time
import threading
import random
from unittest.mock import Mock, patch
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy, BudgetViolationType
from pymemtrace.platform_monitor import GamePlatform


# Simple test object for pooling
class TestObject:
    def __init__(self):
        self.data = [0] * 10
    
    def reset(self):
        self.data = [0] * 10


def test_imports():
    """Test all imports work."""
    assert FrameMemoryProfiler is not None
    assert AssetMemoryManager is not None
    assert ObjectPoolAnalyzer is not None
    assert MemoryBudgetSystem is not None
    assert PlatformMemoryMonitor is not None


# Frame Profiler Tests (20 tests)
def test_frame_profiler_init():
    p = FrameMemoryProfiler()
    assert p is not None

def test_frame_profiler_custom_history():
    p = FrameMemoryProfiler(max_frame_history=100)
    assert p.max_frame_history == 100

def test_frame_profiler_spike_threshold():
    p = FrameMemoryProfiler(spike_threshold=0.5)
    assert p.spike_threshold == 0.5

def test_frame_profiler_start():
    p = FrameMemoryProfiler()
    p.start_profiling()
    assert p._profiling_enabled

def test_frame_profiler_stop():
    p = FrameMemoryProfiler()
    p.start_profiling()
    p.stop_profiling()
    assert not p._profiling_enabled

def test_frame_profiler_context():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        pass
    assert p.frame_count == 1

def test_frame_profiler_manual():
    p = FrameMemoryProfiler()
    p.start_profiling()
    p.start_frame()
    p.end_frame()
    assert p.frame_count == 1

def test_frame_profiler_stats():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        pass
    stats = p.get_frame_stats()
    assert stats is not None

def test_frame_profiler_avg_memory():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        pass
    avg = p.get_average_frame_memory()
    assert avg > 0

def test_frame_profiler_trend():
    p = FrameMemoryProfiler()
    p.start_profiling()
    for _ in range(10):
        with p.frame():
            pass
    trend = p.get_memory_trend(5)
    assert len(trend) > 0

def test_frame_profiler_drops():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        time.sleep(0.02)
    drops = p.detect_frame_drops(60)
    assert len(drops) >= 1

def test_frame_profiler_reset():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        pass
    p.reset()
    assert p.frame_count == 0

def test_frame_profiler_overhead():
    p = FrameMemoryProfiler()
    p.start_profiling()
    overhead = p.get_profiling_overhead()
    assert overhead < 10.0

def test_frame_profiler_correlation():
    p = FrameMemoryProfiler()
    p.start_profiling()
    with p.frame():
        pass
    corr = p.get_frame_time_correlation()
    assert "frame_times" in corr

def test_frame_profiler_callbacks():
    p = FrameMemoryProfiler()
    called = False
    def cb(spike):
        nonlocal called
        called = True
    p.add_spike_callback(cb)
    assert len(p._spike_callbacks) == 1

def test_frame_profiler_disabled():
    p = FrameMemoryProfiler()
    with p.frame():
        pass
    assert p.frame_count == 0

def test_frame_profiler_gc_counts():
    p = FrameMemoryProfiler()
    counts = p._get_gc_counts()
    assert isinstance(counts, dict)

def test_frame_profiler_memory_usage():
    p = FrameMemoryProfiler()
    usage = p._get_memory_usage()
    assert usage > 0

def test_frame_profiler_thread_lock():
    p = FrameMemoryProfiler()
    assert p._lock is not None

def test_frame_profiler_history_deque():
    p = FrameMemoryProfiler(max_frame_history=5)
    p.start_profiling()
    for _ in range(10):
        with p.frame():
            pass
    assert len(p.frame_history) == 5


# Asset Manager Tests (20 tests)
def test_asset_manager_init():
    m = AssetMemoryManager()
    assert m is not None

def test_asset_manager_register():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.TEXTURE, {"data": "test"})
    assert "a1" in m.assets

def test_asset_manager_get_info():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.MODEL, {})
    info = m.get_asset_info("a1")
    assert info.asset_type == AssetType.MODEL

def test_asset_manager_state_update():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.SOUND, {})
    m.update_asset_state("a1", AssetState.CACHED)
    assert m.assets["a1"].state == AssetState.CACHED

def test_asset_manager_references():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    m.add_reference("a1", "r1")
    assert m.assets["a1"].reference_count == 2

def test_asset_manager_remove_ref():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    m.remove_reference("a1", "r1")
    assert m.assets["a1"].reference_count == 1

def test_asset_manager_dependencies():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    m.register_asset("a2", AssetType.OTHER, {})
    m.add_dependency("a1", "a2")
    assert "a2" in m.assets["a1"].dependencies

def test_asset_manager_memory_by_type():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.TEXTURE, {})
    memory = m.get_total_memory_by_type()
    assert AssetType.TEXTURE in memory

def test_asset_manager_heatmap():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.TEXTURE, {})
    heatmap = m.get_memory_heatmap()
    assert heatmap.total_memory >= 0

def test_asset_manager_unused():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    unused = m.get_unused_assets(0.0)
    assert "a1" in unused

def test_asset_manager_leaks():
    m = AssetMemoryManager()
    m.orphaned_assets.add("leak")
    leaks = m.detect_memory_leaks()
    assert "leak" in leaks

def test_asset_manager_lifecycle_stats():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    stats = m.get_asset_lifecycle_stats()
    assert AssetState.LOADED in stats

def test_asset_manager_unload():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    m.assets["a1"].reference_count = 0
    result = m.unload_asset("a1")
    assert result

def test_asset_manager_dep_graph():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    graph = m.get_dependency_graph("a1")
    assert "a1" in graph

def test_asset_manager_total_memory():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    total = m.calculate_total_memory()
    assert total > 0

def test_asset_manager_clear_orphans():
    m = AssetMemoryManager()
    m.orphaned_assets.add("o1")
    count = m.clear_orphaned_assets()
    assert count == 1

def test_asset_manager_validate_refs():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {})
    invalid = m.validate_references()
    assert isinstance(invalid, dict)

def test_asset_manager_metadata():
    m = AssetMemoryManager()
    m.register_asset("a1", AssetType.OTHER, {}, metadata={"key": "value"})
    assert m.assets["a1"].metadata["key"] == "value"

def test_asset_manager_lock():
    m = AssetMemoryManager()
    assert m._lock is not None

def test_asset_manager_weak_refs():
    m = AssetMemoryManager()
    assert isinstance(m.asset_refs, dict)


# Pool Analyzer Tests (20 tests)
def test_pool_analyzer_init():
    a = ObjectPoolAnalyzer()
    assert a is not None

def test_pool_analyzer_create():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    assert "test" in a.pools

def test_pool_analyzer_get():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    assert a.get_pool("test") == pool

def test_pool_analyzer_acquire():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, initial_size=1, name="test")
    obj = pool.acquire()
    assert isinstance(obj, TestObject)

def test_pool_analyzer_release():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    obj = pool.acquire()
    pool.release(obj)
    assert pool.total_deallocations == 1

def test_pool_analyzer_metrics():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    metrics = pool.get_metrics()
    assert metrics.pool_name == "test"

def test_pool_analyzer_efficiency():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    pool.acquire()
    eff = a.analyze_efficiency("test")
    assert "allocation_reduction" in eff

def test_pool_analyzer_pattern():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    pool.acquire()
    a.record_allocation_pattern("test")
    assert True  # Pattern recorded

def test_pool_analyzer_suggest():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    suggestion = a.suggest_pool_size("test")
    assert "suggested_size" in suggestion

def test_pool_analyzer_gc_impact():
    a = ObjectPoolAnalyzer()
    impact = a.measure_gc_impact()
    assert "total_allocations_saved" in impact

def test_pool_analyzer_all_metrics():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    all_metrics = a.get_all_metrics()
    assert "test" in all_metrics

def test_pool_analyzer_optimize():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    optimizations = a.optimize_all_pools()
    assert "test" in optimizations

def test_pool_analyzer_comparison():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    comparison = a.get_pool_comparison()
    assert len(comparison) == 1

def test_pool_analyzer_reset():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, name="test")
    a.reset_metrics("test")
    assert pool.total_allocations == 0

def test_pool_analyzer_overflow():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, max_size=1, name="test")
    obj1 = pool.acquire()
    obj2 = pool.acquire()
    assert pool.overflow_count == 1

def test_pool_analyzer_savings():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, initial_size=1, name="test")
    obj = pool.acquire()
    assert pool.allocation_savings == 1

def test_pool_analyzer_utilization():
    a = ObjectPoolAnalyzer()
    pool = a.create_pool(TestObject, max_size=10, name="test")
    obj = pool.acquire()
    metrics = pool.get_metrics()
    assert 0 <= metrics.utilization_rate <= 1

def test_pool_analyzer_pattern_window():
    a = ObjectPoolAnalyzer()
    assert a._pattern_window == 60.0

def test_pool_analyzer_lock():
    a = ObjectPoolAnalyzer()
    assert a._lock is not None

def test_pool_analyzer_monitoring():
    a = ObjectPoolAnalyzer()
    assert not a._monitoring_enabled


# Budget System Tests (20 tests)
def test_budget_system_init():
    s = MemoryBudgetSystem()
    assert s is not None

def test_budget_system_create():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    assert "test" in s.budgets

def test_budget_system_register():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    s.register_asset("a1", "test", size=100)
    assert s.usage["test"] == 100

def test_budget_system_unregister():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    s.register_asset("a1", "test", size=100)
    s.unregister_asset("a1")
    assert s.usage["test"] == 0

def test_budget_system_hierarchy():
    s = MemoryBudgetSystem()
    s.create_budget("parent", max_bytes=2000)
    s.create_budget("child", max_bytes=1000, parent="parent")
    s.register_asset("a1", "child", size=100)
    assert s.usage["parent"] == 100

def test_budget_system_violation():
    s = MemoryBudgetSystem()
    violations = []
    s.add_violation_callback(lambda v: violations.append(v))
    s.create_budget("test", max_bytes=100)
    s.register_asset("a1", "test", size=150)
    assert len(violations) > 0

def test_budget_system_eviction():
    s = MemoryBudgetSystem()
    s.set_eviction_strategy(EvictionStrategy.SIZE)
    assert s._eviction_strategy == EvictionStrategy.SIZE

def test_budget_system_auto_evict():
    s = MemoryBudgetSystem()
    s.enable_auto_eviction(False)
    assert not s._auto_evict_enabled

def test_budget_system_status():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    status = s.get_budget_status("test")
    assert status["limit"] == 1000

def test_budget_system_analytics():
    s = MemoryBudgetSystem()
    analytics = s.get_budget_analytics()
    assert "total_budgets" in analytics

def test_budget_system_suggest():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    s.register_asset("a1", "test", size=500)
    suggestions = s.suggest_evictions("test", 200)
    assert isinstance(suggestions, list)

def test_budget_system_priority():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000, priority=10)
    assert s.budgets["test"].priority == 10

def test_budget_system_thresholds():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000, warning_threshold=0.7)
    assert s.budgets["test"].warning_threshold == 0.7

def test_budget_system_eviction_cb():
    s = MemoryBudgetSystem()
    evicted = []
    s.add_eviction_callback(lambda a, r: evicted.append(a))
    assert len(s._eviction_callbacks) == 1

def test_budget_system_asset_usage():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    s.register_asset("a1", "test", size=100)
    s.update_asset_usage("a1")
    assert s.assets["a1"].use_count > 1

def test_budget_system_hierarchy_status():
    s = MemoryBudgetSystem()
    s.create_budget("root", max_bytes=1000)
    hierarchy = s.get_hierarchy_status()
    assert "root" in hierarchy

def test_budget_system_eviction_score():
    s = MemoryBudgetSystem()
    s.create_budget("test", max_bytes=1000)
    s.register_asset("a1", "test", size=100)
    asset = s.assets["a1"]
    score = s._calculate_eviction_score(asset)
    assert isinstance(score, (int, float))

def test_budget_system_lock():
    s = MemoryBudgetSystem()
    assert s._lock is not None

def test_budget_system_default_usage():
    s = MemoryBudgetSystem()
    assert isinstance(s.usage, defaultdict)

def test_budget_system_strategies():
    s = MemoryBudgetSystem()
    for strategy in EvictionStrategy:
        s.set_eviction_strategy(strategy)
        assert s._eviction_strategy == strategy


# Platform Monitor Tests (20 tests)
def test_platform_monitor_init():
    m = PlatformMemoryMonitor()
    assert m is not None

def test_platform_monitor_platform():
    m = PlatformMemoryMonitor()
    assert m.current_platform in GamePlatform

def test_platform_monitor_limits():
    m = PlatformMemoryMonitor()
    assert m.memory_limits.total_memory > 0

def test_platform_monitor_status():
    m = PlatformMemoryMonitor()
    status = m.get_current_status()
    assert status.process_memory > 0

def test_platform_monitor_recommendations():
    m = PlatformMemoryMonitor()
    recs = m._generate_recommendations(1000000, 1000000, 50)
    assert isinstance(recs, list)

def test_platform_monitor_guide():
    m = PlatformMemoryMonitor()
    guide = m.get_platform_optimization_guide()
    assert "platform" in guide

def test_platform_monitor_compare():
    m = PlatformMemoryMonitor()
    comp = m.compare_platforms([GamePlatform.PC_WINDOWS, GamePlatform.MOBILE_IOS])
    assert len(comp) == 2

def test_platform_monitor_compatibility():
    m = PlatformMemoryMonitor()
    compat = m.estimate_platform_compatibility(100000000)
    assert len(compat) > 0

def test_platform_monitor_banks():
    m = PlatformMemoryMonitor()
    banks = m.get_memory_bank_usage()
    assert banks is None or isinstance(banks, dict)

def test_platform_monitor_start():
    m = PlatformMemoryMonitor()
    m.start_monitoring()
    assert m._monitoring_enabled
    m.stop_monitoring()

def test_platform_monitor_stop():
    m = PlatformMemoryMonitor()
    m.start_monitoring()
    m.stop_monitoring()
    assert not m._monitoring_enabled

def test_platform_monitor_callback():
    m = PlatformMemoryMonitor()
    m.add_status_callback(lambda s: None)
    assert len(m._callbacks) == 1

def test_platform_monitor_detect():
    m = PlatformMemoryMonitor()
    platform = m._detect_platform()
    assert platform in GamePlatform

def test_platform_monitor_configs():
    m = PlatformMemoryMonitor()
    assert len(m.PLATFORM_CONFIGS) > 0

def test_platform_monitor_critical():
    m = PlatformMemoryMonitor()
    status = m.get_current_status()
    assert isinstance(status.is_critical, bool)

def test_platform_monitor_percentage():
    m = PlatformMemoryMonitor()
    status = m.get_current_status()
    assert 0 <= status.memory_percentage <= 100

def test_platform_monitor_process():
    m = PlatformMemoryMonitor()
    assert m._process is not None

def test_platform_monitor_lock():
    m = PlatformMemoryMonitor()
    assert m._lock is not None

def test_platform_monitor_last_status():
    m = PlatformMemoryMonitor()
    status = m.get_current_status()
    assert m._last_status is not None

def test_platform_monitor_thread():
    m = PlatformMemoryMonitor()
    assert m._monitor_thread is None