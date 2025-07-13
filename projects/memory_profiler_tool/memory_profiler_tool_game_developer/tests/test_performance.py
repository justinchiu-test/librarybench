"""Performance and stress tests for PyMemTrace."""

import pytest
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from pymemtrace import (
    FrameMemoryProfiler, AssetMemoryManager, ObjectPoolAnalyzer,
    MemoryBudgetSystem, PlatformMemoryMonitor
)
from pymemtrace.asset_manager import AssetType, AssetState
from pymemtrace.budget_system import EvictionStrategy


class TestPerformanceRequirements:
    """Tests to verify performance requirements are met."""
    
    def test_frame_profiler_overhead_requirement(self):
        """Test frame profiler meets <0.5ms overhead requirement."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        # Measure overhead over multiple frames
        overheads = []
        for _ in range(100):
            overhead = profiler.get_profiling_overhead()
            overheads.append(overhead)
        
        avg_overhead = sum(overheads) / len(overheads)
        assert avg_overhead < 0.5  # Must be less than 0.5ms
    
    def test_60fps_support(self):
        """Test profiler can handle 60 FPS without drops."""
        profiler = FrameMemoryProfiler()
        profiler.start_profiling()
        
        frame_time_ms = 1000.0 / 60  # ~16.67ms per frame
        
        start = time.perf_counter()
        for _ in range(60):  # 1 second of frames
            frame_start = time.perf_counter()
            
            with profiler.frame():
                # Simulate some work
                _ = [i for i in range(1000)]
            
            frame_duration = (time.perf_counter() - frame_start) * 1000
            assert frame_duration < frame_time_ms
        
        total_time = time.perf_counter() - start
        assert total_time < 1.1  # Should complete in ~1 second
    
    def test_asset_tracking_10k_objects(self):
        """Test asset manager can track 10,000+ objects efficiently."""
        manager = AssetMemoryManager()
        
        start = time.perf_counter()
        
        # Register 10,000 assets
        for i in range(10000):
            manager.register_asset(
                f"asset_{i}",
                AssetType.OTHER,
                {"id": i, "data": f"asset_data_{i}"}
            )
        
        registration_time = time.perf_counter() - start
        assert registration_time < 5.0  # Should complete in under 5 seconds
        
        # Test query performance
        query_start = time.perf_counter()
        for i in range(0, 10000, 100):  # Sample queries
            info = manager.get_asset_info(f"asset_{i}")
            assert info is not None
        
        query_time = time.perf_counter() - query_start
        assert query_time < 0.1  # Queries should be fast
    
    def test_pool_monitoring_overhead(self):
        """Test pool monitoring has <0.1ms overhead."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(object, initial_size=100, max_size=1000)
        
        # Measure overhead
        overheads = []
        for _ in range(100):
            start = time.perf_counter()
            obj = pool.acquire()
            pool.release(obj)
            overhead = (time.perf_counter() - start) * 1000
            overheads.append(overhead)
        
        avg_overhead = sum(overheads) / len(overheads)
        assert avg_overhead < 0.1  # Must be less than 0.1ms
    
    def test_memory_snapshot_generation(self):
        """Test memory snapshot generation <5ms."""
        manager = AssetMemoryManager()
        
        # Register many assets
        for i in range(1000):
            manager.register_asset(f"asset_{i}", AssetType.OTHER, {"data": i})
        
        # Measure snapshot generation
        start = time.perf_counter()
        heatmap = manager.get_memory_heatmap(top_n=100)
        snapshot_time = (time.perf_counter() - start) * 1000
        
        assert snapshot_time < 5.0  # Must be less than 5ms
        assert heatmap is not None
    
    def test_1gb_asset_library_support(self):
        """Test support for 1GB+ asset libraries."""
        manager = AssetMemoryManager()
        budget_system = MemoryBudgetSystem()
        
        # Create large budget
        budget_system.create_budget("assets", max_bytes=1024*1024*1024)  # 1GB
        
        # Simulate large assets
        total_size = 0
        asset_count = 0
        
        while total_size < 1024*1024*1024:  # 1GB
            size = random.randint(1024*1024, 10*1024*1024)  # 1-10MB
            asset_id = f"large_asset_{asset_count}"
            
            manager.register_asset(asset_id, AssetType.TEXTURE, {"size": size})
            budget_system.register_asset(asset_id, "assets", size=size)
            
            total_size += size
            asset_count += 1
        
        assert total_size >= 1024*1024*1024
        assert budget_system.usage["assets"] >= 1024*1024*1024


class TestStressScenarios:
    """Stress tests for extreme usage scenarios."""
    
    def test_rapid_frame_profiling(self):
        """Test rapid frame profiling at 120+ FPS."""
        profiler = FrameMemoryProfiler(max_frame_history=500)
        profiler.start_profiling()
        
        # Simulate 120 FPS for 2 seconds
        start = time.perf_counter()
        frame_count = 0
        
        while time.perf_counter() - start < 2.0:
            with profiler.frame():
                frame_count += 1
                # Minimal work to maintain high FPS
                pass
        
        fps = frame_count / 2.0
        assert fps >= 120  # Should achieve 120+ FPS
        assert profiler.frame_count == frame_count
    
    def test_concurrent_asset_operations(self):
        """Test concurrent asset registration and queries."""
        manager = AssetMemoryManager()
        
        def register_assets(start_id):
            for i in range(100):
                manager.register_asset(
                    f"concurrent_{start_id}_{i}",
                    AssetType.OTHER,
                    {"thread": start_id}
                )
        
        def query_assets():
            for _ in range(200):
                asset_id = f"concurrent_{random.randint(0, 9)}_{random.randint(0, 99)}"
                manager.get_asset_info(asset_id)
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit registration tasks
            reg_futures = [executor.submit(register_assets, i) for i in range(10)]
            # Submit query tasks
            query_futures = [executor.submit(query_assets) for _ in range(5)]
            
            # Wait for completion
            for f in reg_futures + query_futures:
                f.result()
        
        # Verify all assets registered
        assert len(manager.assets) == 1000
    
    def test_massive_budget_hierarchy(self):
        """Test deep budget hierarchy."""
        system = MemoryBudgetSystem()
        
        # Create deep hierarchy
        parent = "root"
        system.create_budget(parent, max_bytes=1024*1024*1024)
        
        for i in range(50):  # 50 levels deep
            child = f"level_{i}"
            system.create_budget(child, max_bytes=1024*1024*100, parent=parent)
            parent = child
        
        # Register asset at deepest level
        system.register_asset("deep_asset", f"level_49", size=1024*1024)
        
        # Should propagate to root
        assert system.usage["root"] == 1024*1024
    
    def test_pool_allocation_storm(self):
        """Test pool under allocation storm."""
        analyzer = ObjectPoolAnalyzer()
        pool = analyzer.create_pool(object, initial_size=10, max_size=100)
        
        acquired = []
        
        # Rapid acquire/release cycles
        for _ in range(1000):
            # Acquire random number
            for _ in range(random.randint(1, 20)):
                acquired.append(pool.acquire())
            
            # Release random number
            release_count = random.randint(0, len(acquired))
            for _ in range(release_count):
                if acquired:
                    pool.release(acquired.pop())
        
        # Pool should still be functional
        metrics = pool.get_metrics()
        assert metrics.allocation_savings > 0
    
    def test_memory_budget_cascade_eviction(self):
        """Test cascading evictions under memory pressure."""
        system = MemoryBudgetSystem()
        system.set_eviction_strategy(EvictionStrategy.SIZE)
        
        evicted = []
        system.add_eviction_callback(lambda a, r: evicted.append(a))
        
        # Create tight budget
        system.create_budget("tight", max_bytes=10000)
        
        # Fill with assets
        for i in range(20):
            system.register_asset(
                f"asset_{i}",
                "tight",
                size=1000,
                priority=i % 5
            )
        
        # Should have evicted half
        assert len(evicted) >= 10
        assert system.usage["tight"] <= 10000
    
    def test_platform_monitor_all_platforms(self):
        """Test monitor with all platform configurations."""
        monitor = PlatformMemoryMonitor()
        
        results = {}
        for platform in PlatformMemoryMonitor.PLATFORM_CONFIGS:
            monitor.current_platform = platform
            monitor.memory_limits = monitor._get_platform_limits()
            
            status = monitor.get_current_status()
            guide = monitor.get_platform_optimization_guide()
            
            results[platform] = {
                "status": status,
                "guide": guide
            }
        
        assert len(results) == len(PlatformMemoryMonitor.PLATFORM_CONFIGS)
    
    def test_leak_detection_performance(self):
        """Test leak detection with many assets."""
        manager = AssetMemoryManager()
        
        # Create complex dependency graph
        for i in range(100):
            manager.register_asset(f"node_{i}", AssetType.OTHER, {})
            
            # Add random dependencies
            for _ in range(random.randint(0, 5)):
                dep = random.randint(0, 99)
                if dep != i:
                    manager.add_dependency(f"node_{i}", f"node_{dep}")
        
        # Measure leak detection performance
        start = time.perf_counter()
        leaks = manager.detect_memory_leaks()
        detection_time = time.perf_counter() - start
        
        assert detection_time < 1.0  # Should complete in under 1 second
    
    def test_continuous_profiling_24h_simulation(self):
        """Test continuous profiling stability (simulated)."""
        profiler = FrameMemoryProfiler(max_frame_history=1000)
        profiler.start_profiling()
        
        # Simulate 1 hour at 60 FPS (instead of 24h for test speed)
        frames_per_hour = 60 * 60 * 60  # 216,000 frames
        
        # Sample test: run for 1000 frames
        for i in range(1000):
            with profiler.frame():
                if i % 100 == 0:
                    # Periodic checks
                    assert len(profiler.frame_history) <= 1000
                    assert profiler.get_average_frame_memory() > 0
        
        assert profiler.frame_count == 1000
    
    def test_mixed_workload_simulation(self):
        """Test realistic mixed game workload."""
        # Initialize all components
        frame_profiler = FrameMemoryProfiler()
        asset_manager = AssetMemoryManager()
        pool_analyzer = ObjectPoolAnalyzer()
        budget_system = MemoryBudgetSystem()
        platform_monitor = PlatformMemoryMonitor()
        
        # Setup
        frame_profiler.start_profiling()
        budget_system.create_budget("game", max_bytes=512*1024*1024)
        particle_pool = pool_analyzer.create_pool(object, max_size=1000, name="particles")
        
        # Simulate game loop
        for frame in range(100):
            with frame_profiler.frame():
                # Asset loading/unloading
                if frame % 10 == 0:
                    asset_manager.register_asset(f"texture_{frame}", AssetType.TEXTURE, {"frame": frame})
                    budget_system.register_asset(f"texture_{frame}", "game", size=1024*1024)
                
                # Object pooling
                particles = []
                for _ in range(random.randint(10, 50)):
                    particles.append(particle_pool.acquire())
                
                for p in particles:
                    particle_pool.release(p)
                
                # Platform check
                if frame % 30 == 0:
                    status = platform_monitor.get_current_status()
                    assert not status.is_critical
        
        # Verify system health
        assert frame_profiler.frame_count == 100
        assert len(asset_manager.assets) >= 10
        assert particle_pool.allocation_savings > 0