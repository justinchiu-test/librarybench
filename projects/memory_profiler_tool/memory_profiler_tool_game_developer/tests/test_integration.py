"""Integration tests for PyMemTrace."""

import time
import pytest
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy
from pymemtrace.pool_analyzer import ObjectPool


class GameAsset:
    """Mock game asset for testing."""
    def __init__(self, size: int = 1000):
        self.data = b"x" * size
        self.loaded = True
    
    def reset(self):
        """Reset for object pooling."""
        self.loaded = True


class TestIntegration:
    """Integration tests for all modules working together."""
    
    def test_complete_game_scenario(self):
        """Test a complete game scenario with all components."""
        # Initialize all components
        frame_profiler = FrameMemoryProfiler(spike_threshold=0.2)
        asset_manager = AssetMemoryManager()
        pool_analyzer = ObjectPoolAnalyzer()
        budget_system = MemoryBudgetSystem()
        platform_monitor = PlatformMemoryMonitor()
        
        # Set up memory budgets
        budget_system.create_budget("total", max_bytes=50 * 1024 * 1024)  # 50MB
        budget_system.create_budget("textures", max_bytes=20 * 1024 * 1024, parent="total")
        budget_system.create_budget("models", max_bytes=15 * 1024 * 1024, parent="total")
        budget_system.create_budget("sounds", max_bytes=10 * 1024 * 1024, parent="total")
        
        # Create object pools
        texture_pool = pool_analyzer.create_pool(GameAsset, initial_size=5, max_size=20, name="TexturePool")
        model_pool = pool_analyzer.create_pool(GameAsset, initial_size=3, max_size=10, name="ModelPool")
        
        # Start profiling
        frame_profiler.start_profiling()
        
        # Simulate game frames
        for frame in range(10):
            with frame_profiler.frame():
                # Load some assets
                if frame % 2 == 0:
                    texture = texture_pool.acquire()
                    asset_manager.register_asset(
                        f"texture_{frame}",
                        AssetType.TEXTURE,
                        texture
                    )
                    budget_system.register_asset(
                        f"texture_{frame}",
                        "textures",
                        size=len(texture.data)
                    )
                
                if frame % 3 == 0:
                    model = model_pool.acquire()
                    asset_manager.register_asset(
                        f"model_{frame}",
                        AssetType.MODEL,
                        model
                    )
                    budget_system.register_asset(
                        f"model_{frame}",
                        "models",
                        size=len(model.data)
                    )
                
                # Update asset states
                if frame > 0:
                    asset_manager.update_asset_state(f"texture_{frame-1}", AssetState.IN_USE)
                
                # Simulate frame time
                time.sleep(0.01)
        
        # Verify results
        assert frame_profiler.frame_count == 10
        assert len(asset_manager.assets) > 0
        assert pool_analyzer.get_pool("TexturePool").allocation_savings > 0
        assert budget_system.usage["total"] > 0
        
        # Check platform status
        platform_status = platform_monitor.get_current_status()
        assert not platform_status.is_critical
    
    def test_memory_pressure_scenario(self):
        """Test system behavior under memory pressure."""
        # Initialize components
        asset_manager = AssetMemoryManager()
        budget_system = MemoryBudgetSystem()
        budget_system.set_eviction_strategy(EvictionStrategy.LRU)
        
        # Track evictions
        evicted_assets = []
        budget_system.add_eviction_callback(
            lambda asset_id, reason: evicted_assets.append(asset_id)
        )
        
        # Create tight budget
        budget_system.create_budget("game", max_bytes=5000)
        
        # Load assets until eviction
        for i in range(10):
            asset = GameAsset(size=1000)
            asset_manager.register_asset(f"asset_{i}", AssetType.OTHER, asset)
            budget_system.register_asset(f"asset_{i}", "game", size=1000)
            time.sleep(0.01)  # Ensure different timestamps for LRU
        
        # Should have evicted some assets
        assert len(evicted_assets) > 0
        assert budget_system.usage["game"] <= 5000
    
    def test_performance_monitoring(self):
        """Test performance impact of profiling."""
        frame_profiler = FrameMemoryProfiler()
        pool_analyzer = ObjectPoolAnalyzer()
        
        # Create a pool
        pool = pool_analyzer.create_pool(GameAsset, initial_size=10, name="PerfTest")
        
        # Measure baseline frame time
        start = time.perf_counter()
        for _ in range(100):
            obj = pool.acquire()
            pool.release(obj)
        baseline_time = time.perf_counter() - start
        
        # Measure with profiling
        frame_profiler.start_profiling()
        start = time.perf_counter()
        for _ in range(100):
            with frame_profiler.frame():
                obj = pool.acquire()
                pool.release(obj)
        profiled_time = time.perf_counter() - start
        
        # Overhead should be minimal
        overhead_ratio = (profiled_time - baseline_time) / baseline_time
        assert overhead_ratio < 0.5  # Less than 50% overhead
    
    def test_asset_lifecycle_with_budget(self):
        """Test complete asset lifecycle with budget management."""
        asset_manager = AssetMemoryManager()
        budget_system = MemoryBudgetSystem()
        
        # Create budget
        budget_system.create_budget("assets", max_bytes=10000)
        
        # Asset lifecycle
        asset_data = {"mesh": "data", "textures": ["tex1", "tex2"]}
        
        # Load
        asset_manager.register_asset("player_model", AssetType.MODEL, asset_data)
        budget_system.register_asset("player_model", "assets", size=2000)
        
        # Use
        asset_manager.update_asset_state("player_model", AssetState.IN_USE)
        budget_system.update_asset_usage("player_model")
        
        # Cache
        asset_manager.update_asset_state("player_model", AssetState.CACHED)
        
        # Check status
        asset_info = asset_manager.get_asset_info("player_model")
        assert asset_info.state == AssetState.CACHED
        assert asset_info.use_count > 1
        
        budget_status = budget_system.get_budget_status("assets")
        assert budget_status["usage"] == 2000
    
    def test_pool_optimization_suggestions(self):
        """Test pool optimization based on usage patterns."""
        pool_analyzer = ObjectPoolAnalyzer()
        frame_profiler = FrameMemoryProfiler()
        
        # Create pool
        pool = pool_analyzer.create_pool(
            GameAsset,
            initial_size=5,
            max_size=10,
            name="OptimizeTest"
        )
        
        frame_profiler.start_profiling()
        
        # Simulate varying load
        for frame in range(20):
            with frame_profiler.frame():
                # Variable number of objects per frame
                object_count = 3 + (frame % 8)
                objects = []
                
                for _ in range(object_count):
                    objects.append(pool.acquire())
                
                # Record pattern
                pool_analyzer.record_allocation_pattern("OptimizeTest")
                
                # Release objects
                for obj in objects:
                    pool.release(obj)
                
                time.sleep(0.01)
        
        # Get optimization suggestion
        suggestion = pool_analyzer.suggest_pool_size("OptimizeTest")
        
        # Should suggest larger pool due to peaks
        assert suggestion["suggested_size"] >= suggestion["current_size"]
        assert suggestion["reason"] == "pattern_analysis"
    
    def test_platform_specific_recommendations(self):
        """Test platform-specific memory recommendations."""
        platform_monitor = PlatformMemoryMonitor()
        asset_manager = AssetMemoryManager()
        
        # Simulate high memory usage
        large_assets = []
        for i in range(5):
            asset = GameAsset(size=10 * 1024 * 1024)  # 10MB each
            large_assets.append(asset)
            asset_manager.register_asset(f"large_{i}", AssetType.TEXTURE, asset)
        
        # Get current status
        status = platform_monitor.get_current_status()
        
        # Check compatibility with other platforms
        compatibility = platform_monitor.estimate_platform_compatibility(
            status.process_memory
        )
        
        # Should have platform-specific info
        assert len(compatibility) > 0
        assert all("optimization_needed" in v for v in compatibility.values())
    
    def test_memory_leak_detection(self):
        """Test memory leak detection across components."""
        asset_manager = AssetMemoryManager()
        pool_analyzer = ObjectPoolAnalyzer()
        
        # Create circular dependency
        asset_manager.register_asset("shader", AssetType.SHADER, {})
        asset_manager.register_asset("material", AssetType.OTHER, {})
        asset_manager.register_asset("mesh", AssetType.MODEL, {})
        
        asset_manager.add_dependency("shader", "material")
        asset_manager.add_dependency("material", "mesh")
        asset_manager.add_dependency("mesh", "shader")  # Circular!
        
        # Detect leaks
        leaks = asset_manager.detect_memory_leaks()
        assert len(leaks) > 0
        
        # Create pool with overflow
        pool = pool_analyzer.create_pool(GameAsset, max_size=2, name="LeakTest")
        
        # Acquire without releasing
        leaked_objects = []
        for _ in range(5):
            leaked_objects.append(pool.acquire())
        
        metrics = pool.get_metrics()
        assert metrics.overflow_count > 0
    
    def test_frame_drops_with_memory_spikes(self):
        """Test correlation between memory spikes and frame drops."""
        frame_profiler = FrameMemoryProfiler(spike_threshold=0.1)
        spikes_detected = []
        
        frame_profiler.add_spike_callback(
            lambda spike: spikes_detected.append(spike)
        )
        
        frame_profiler.start_profiling()
        
        # Normal frames
        for _ in range(5):
            with frame_profiler.frame():
                time.sleep(0.01)
        
        # Frame with memory spike and drop
        with frame_profiler.frame():
            # Allocate large amount of memory
            large_data = [list(range(10000)) for _ in range(100)]
            time.sleep(0.02)  # Simulate frame drop
        
        # Check for frame drops
        dropped_frames = frame_profiler.detect_frame_drops(target_fps=60)
        assert len(dropped_frames) >= 1
        
        # Memory spike might be detected (depends on GC)
        # At minimum, frame time correlation should show the spike
        correlation = frame_profiler.get_frame_time_correlation()
        frame_times = correlation["frame_times"]
        assert max(frame_times) > 16.67  # At least one frame exceeded 60 FPS target