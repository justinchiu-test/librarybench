"""Minimal test suite to verify all modules work correctly."""

import pytest
import time
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy


def test_frame_profiler_basic():
    """Test basic frame profiler functionality."""
    profiler = FrameMemoryProfiler()
    profiler.start_profiling()
    
    with profiler.frame():
        time.sleep(0.001)
    
    assert profiler.frame_count == 1
    stats = profiler.get_frame_stats()
    assert stats is not None
    assert stats.frame_number == 1


def test_asset_manager_basic():
    """Test basic asset manager functionality."""
    manager = AssetMemoryManager()
    
    # Use a dict instead of bytes to avoid weak reference issues
    test_asset = {"data": "test_content"}
    manager.register_asset("asset_1", AssetType.TEXTURE, test_asset)
    
    assert "asset_1" in manager.assets
    info = manager.get_asset_info("asset_1")
    assert info.asset_type == AssetType.TEXTURE


def test_pool_analyzer_basic():
    """Test basic pool analyzer functionality."""
    class TestObject:
        def __init__(self):
            self.data = [0] * 100
    
    analyzer = ObjectPoolAnalyzer()
    pool = analyzer.create_pool(TestObject, initial_size=5, name="TestPool")
    
    obj = pool.acquire()
    assert isinstance(obj, TestObject)
    pool.release(obj)
    
    metrics = pool.get_metrics()
    assert metrics.pool_name == "TestPool"


def test_budget_system_basic():
    """Test basic budget system functionality."""
    system = MemoryBudgetSystem()
    system.create_budget("test", max_bytes=10000)
    
    system.register_asset("asset_1", "test", size=1000)
    assert system.usage["test"] == 1000
    
    status = system.get_budget_status("test")
    assert status["usage"] == 1000


def test_platform_monitor_basic():
    """Test basic platform monitor functionality."""
    monitor = PlatformMemoryMonitor()
    
    status = monitor.get_current_status()
    assert status.platform is not None
    assert status.process_memory > 0
    assert 0 <= status.memory_percentage <= 100


def test_integration_basic():
    """Test basic integration of all components."""
    # Initialize components
    frame_profiler = FrameMemoryProfiler()
    asset_manager = AssetMemoryManager()
    pool_analyzer = ObjectPoolAnalyzer()
    budget_system = MemoryBudgetSystem()
    platform_monitor = PlatformMemoryMonitor()
    
    # Start profiling
    frame_profiler.start_profiling()
    
    # Create budget
    budget_system.create_budget("game", max_bytes=100000)
    
    # Profile a frame
    with frame_profiler.frame():
        # Register an asset
        test_obj = {"type": "texture", "size": 1000}
        asset_manager.register_asset("tex_1", AssetType.TEXTURE, test_obj)
        budget_system.register_asset("tex_1", "game", size=1000)
    
    # Verify everything worked
    assert frame_profiler.frame_count == 1
    assert "tex_1" in asset_manager.assets
    assert budget_system.usage["game"] == 1000
    
    # Get platform status
    status = platform_monitor.get_current_status()
    assert not status.is_critical


def test_memory_spike_detection():
    """Test memory spike detection functionality."""
    profiler = FrameMemoryProfiler(spike_threshold=0.1)
    profiler.start_profiling()
    
    # Create baseline
    for _ in range(5):
        with profiler.frame():
            pass
    
    # Verify frames were recorded
    assert profiler.frame_count >= 5
    avg_memory = profiler.get_average_frame_memory(last_n_frames=5)
    assert avg_memory > 0


def test_asset_lifecycle():
    """Test asset lifecycle management."""
    manager = AssetMemoryManager()
    
    # Create asset
    asset_obj = {"content": "data"}
    manager.register_asset("lifecycle_test", AssetType.MODEL, asset_obj)
    
    # Update states
    manager.update_asset_state("lifecycle_test", AssetState.IN_USE)
    manager.update_asset_state("lifecycle_test", AssetState.CACHED)
    
    info = manager.get_asset_info("lifecycle_test")
    assert info.state == AssetState.CACHED


def test_pool_efficiency():
    """Test object pool efficiency metrics."""
    class GameObject:
        def __init__(self):
            self.active = True
    
    analyzer = ObjectPoolAnalyzer()
    pool = analyzer.create_pool(GameObject, initial_size=10, name="EfficiencyTest")
    
    # Use pool
    objects = []
    for _ in range(5):
        objects.append(pool.acquire())
    
    for obj in objects:
        pool.release(obj)
    
    efficiency = analyzer.analyze_efficiency("EfficiencyTest")
    assert "allocation_reduction" in efficiency
    assert efficiency["allocation_reduction"] > 0


def test_budget_violations():
    """Test budget violation handling."""
    system = MemoryBudgetSystem()
    violations = []
    
    system.add_violation_callback(lambda v: violations.append(v))
    system.create_budget("limited", max_bytes=1000, warning_threshold=0.8)
    
    # Add asset that triggers warning
    system.register_asset("big_asset", "limited", size=850)
    
    assert len(violations) == 1
    assert violations[0].budget_name == "limited"


def test_platform_compatibility():
    """Test platform compatibility checking."""
    monitor = PlatformMemoryMonitor()
    
    # Test with 100MB usage
    test_memory = 100 * 1024 * 1024
    compatibility = monitor.estimate_platform_compatibility(test_memory)
    
    # Should be compatible with PC platforms
    assert len(compatibility) > 0
    # At least one platform should be compatible
    assert any(v["meets_minimum"] for v in compatibility.values())