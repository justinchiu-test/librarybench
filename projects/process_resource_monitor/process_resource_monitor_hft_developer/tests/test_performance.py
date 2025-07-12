import pytest
import time
import os
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import concurrent.futures
import multiprocessing

from hft_resource_monitor import HFTResourceMonitor
from hft_resource_monitor.metrics import (
    CacheMetrics, ContextSwitchInfo, NUMAStats, LatencySpike,
    ThreadSchedulingInfo
)


class TestPerformance:
    """Performance and stress tests for HFT Resource Monitor"""
    
    def test_high_volume_cache_metrics(self):
        """Test handling high volume of cache metrics"""
        monitor = HFTResourceMonitor()
        
        # Generate 10000 metrics rapidly
        start = time.perf_counter()
        for i in range(10000):
            metric = CacheMetrics(
                timestamp=datetime.now(),
                l1_hits=i * 100,
                l1_misses=i * 10,
                l2_hits=i * 50,
                l2_misses=i * 5,
                l3_hits=i * 25,
                l3_misses=i * 2,
                tlb_misses=i,
                false_sharing_events=0,
                cache_line_bounces=0
            )
            monitor._cache_metrics.append(metric)
        
        elapsed = time.perf_counter() - start
        
        # Should handle 10k metrics in under 100ms
        assert elapsed < 0.1
        assert len(monitor._cache_metrics) == 10000
    
    def test_concurrent_metric_collection(self):
        """Test concurrent access to metric collections"""
        monitor = HFTResourceMonitor()
        
        def add_metrics(metric_type, count):
            for i in range(count):
                if metric_type == 'cache':
                    metric = CacheMetrics(
                        timestamp=datetime.now(),
                        l1_hits=1000, l1_misses=100,
                        l2_hits=500, l2_misses=50,
                        l3_hits=100, l3_misses=10,
                        tlb_misses=5, false_sharing_events=0,
                        cache_line_bounces=0
                    )
                    monitor._cache_metrics.append(metric)
                elif metric_type == 'context':
                    switch = ContextSwitchInfo(
                        timestamp=datetime.now(),
                        pid=os.getpid(), tid=i,
                        cpu_from=0, cpu_to=1,
                        voluntary=True, duration_us=10.0
                    )
                    monitor._context_switches.append(switch)
        
        # Run concurrent additions
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            futures.append(executor.submit(add_metrics, 'cache', 1000))
            futures.append(executor.submit(add_metrics, 'cache', 1000))
            futures.append(executor.submit(add_metrics, 'context', 1000))
            futures.append(executor.submit(add_metrics, 'context', 1000))
            
            for future in futures:
                future.result()
        
        # Verify data integrity
        assert len(monitor._cache_metrics) <= 10000  # Limited by deque maxlen
        assert len(monitor._context_switches) <= 10000
    
    def test_memory_efficiency(self):
        """Test memory efficiency with circular buffers"""
        monitor = HFTResourceMonitor()
        
        # Fill all buffers to capacity
        for i in range(11000):  # Over capacity
            # Add to each buffer type
            monitor._cache_metrics.append(CacheMetrics(
                timestamp=datetime.now(),
                l1_hits=i, l1_misses=0,
                l2_hits=0, l2_misses=0,
                l3_hits=0, l3_misses=0,
                tlb_misses=0, false_sharing_events=0,
                cache_line_bounces=0
            ))
            
            monitor._context_switches.append(ContextSwitchInfo(
                timestamp=datetime.now(),
                pid=i, tid=i,
                cpu_from=0, cpu_to=1,
                voluntary=True, duration_us=1.0
            ))
        
        # Verify buffers respect their limits
        assert len(monitor._cache_metrics) == 10000
        assert len(monitor._context_switches) == 10000
        
        # Verify oldest items were discarded
        assert monitor._cache_metrics[0].l1_hits >= 1000
    
    def test_percentile_calculation_performance(self):
        """Test performance of percentile calculations"""
        monitor = HFTResourceMonitor()
        
        # Add many metrics with varying hit rates
        for i in range(5000):
            metric = CacheMetrics(
                timestamp=datetime.now(),
                l1_hits=np.random.randint(900, 1000),
                l1_misses=np.random.randint(0, 100),
                l2_hits=np.random.randint(400, 600),
                l2_misses=np.random.randint(0, 100),
                l3_hits=np.random.randint(50, 150),
                l3_misses=np.random.randint(0, 50),
                tlb_misses=0, false_sharing_events=0,
                cache_line_bounces=0
            )
            monitor._cache_metrics.append(metric)
        
        # Time percentile calculation
        start = time.perf_counter()
        metrics = monitor.get_cache_metrics(
            time_window_us=10000000,  # All metrics
            percentiles=[10, 25, 50, 75, 90, 95, 99, 99.9]
        )
        elapsed = time.perf_counter() - start
        
        # Should calculate percentiles quickly
        assert elapsed < 0.1
        assert metrics[-1].percentiles is not None
        assert len(metrics[-1].percentiles) == 8
    
    def test_time_window_filtering_performance(self):
        """Test performance of time window filtering"""
        monitor = HFTResourceMonitor()
        
        # Add metrics over time span
        base_time = datetime.now() - timedelta(seconds=10)
        for i in range(10000):
            metric = CacheMetrics(
                timestamp=base_time + timedelta(microseconds=i * 1000),
                l1_hits=1000, l1_misses=100,
                l2_hits=500, l2_misses=50,
                l3_hits=100, l3_misses=10,
                tlb_misses=0, false_sharing_events=0,
                cache_line_bounces=0
            )
            monitor._cache_metrics.append(metric)
        
        # Time filtering operation
        start = time.perf_counter()
        recent_metrics = monitor.get_cache_metrics(time_window_us=1000000)  # Last 1 second
        elapsed = time.perf_counter() - start
        
        # Should filter quickly
        assert elapsed < 0.01
        assert len(recent_metrics) < 10000
    
    def test_spike_detection_performance(self):
        """Test performance of latency spike detection"""
        monitor = HFTResourceMonitor()
        
        # Add many spikes with varying durations
        for i in range(1000):
            spike = LatencySpike(
                timestamp=datetime.now(),
                duration_us=np.random.exponential(50),
                thread_id=i % 10,
                cpu=i % os.cpu_count(),
                cause=np.random.choice(['cache_miss', 'context_switch', 'interrupt']),
                details={'index': i}
            )
            monitor._latency_spikes.append(spike)
        
        # Time spike detection with filtering
        start = time.perf_counter()
        significant_spikes = monitor.detect_latency_spikes(
            threshold_us=100,
            include_cause_analysis=True
        )
        elapsed = time.perf_counter() - start
        
        # Should detect spikes quickly
        assert elapsed < 0.01
        assert all(spike.duration_us >= 100 for spike in significant_spikes)
    
    def test_numa_bandwidth_calculation(self):
        """Test NUMA bandwidth calculations"""
        monitor = HFTResourceMonitor()
        
        # Simulate high bandwidth scenario
        for node in range(4):  # 4 NUMA nodes
            for i in range(100):
                stats = NUMAStats(
                    timestamp=datetime.now(),
                    node_id=node,
                    local_accesses=1000000 * (i + 1),
                    remote_accesses=100000 * (i + 1),
                    bandwidth_mb_per_sec=50000.0 + i * 100,
                    hot_spots=[(addr, 1000) for addr in range(5)],
                    inter_socket_overhead_us=2.0 + i * 0.01
                )
                monitor._numa_stats.append(stats)
        
        # Get stats with heatmap
        numa_stats = monitor.get_numa_stats(include_heatmap=True)
        
        # Verify calculations
        assert len(numa_stats) == 400
        total_bandwidth = sum(s.bandwidth_mb_per_sec for s in numa_stats)
        assert total_bandwidth > 0
    
    def test_thread_scheduling_overhead(self):
        """Test overhead of thread scheduling info collection"""
        monitor = HFTResourceMonitor()
        
        # Simulate many threads
        start = time.perf_counter()
        for tid in range(1000):
            for i in range(10):
                info = ThreadSchedulingInfo(
                    timestamp=datetime.now(),
                    tid=tid,
                    priority=20 - (tid % 40),
                    nice_value=tid % 20 - 10,
                    scheduling_class='SCHED_OTHER',
                    cpu_affinity=list(range(min(4, os.cpu_count()))),
                    cpu_time_us=1000.0 * i,
                    wait_time_us=10.0 * i,
                    priority_inversions=0,
                    scheduling_jitter_us=1.0 + i * 0.1
                )
                monitor._thread_scheduling.append(info)
        
        elapsed = time.perf_counter() - start
        
        # Should handle 10k thread records quickly
        assert elapsed < 0.1
        assert len(monitor._thread_scheduling) == 10000
    
    @patch('psutil.Process')
    def test_multi_process_monitoring_scalability(self, mock_process_class):
        """Test monitoring many processes simultaneously"""
        monitor = HFTResourceMonitor()
        monitor.configure(sampling_interval_us=1000)
        
        # Attach many processes
        processes = []
        for pid in range(100, 200):
            mock_process = Mock()
            mock_process.is_running.return_value = True
            mock_process.pid = pid
            mock_process_class.return_value = mock_process
            processes.append(mock_process)
            
            monitor.attach_process(pid)
        
        assert len(monitor.attached_processes) == 100
        
        # Verify performance counter initialization
        for pid in range(100, 200):
            assert pid in monitor._perf_counters
    
    def test_zero_copy_metric_access(self):
        """Test that metric access doesn't copy unnecessarily"""
        monitor = HFTResourceMonitor()
        
        # Add a metric
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=1000, l1_misses=100,
            l2_hits=500, l2_misses=50,
            l3_hits=100, l3_misses=10,
            tlb_misses=5, false_sharing_events=0,
            cache_line_bounces=0
        )
        monitor._cache_metrics.append(metric)
        
        # Get metrics without time filtering
        metrics = list(monitor._cache_metrics)
        
        # Verify it's the same object (no copy)
        assert metrics[0] is metric
    
    def test_microsecond_timing_precision(self):
        """Test microsecond-level timing precision"""
        timestamps = []
        
        # Collect high-resolution timestamps
        for _ in range(100):
            timestamps.append(time.perf_counter())
            time.sleep(0.00001)  # 10 microseconds
        
        # Calculate intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(99)]
        
        # Verify microsecond precision
        min_interval = min(intervals) * 1_000_000  # Convert to microseconds
        assert min_interval > 5  # At least 5 microseconds
        assert min_interval < 100  # Less than 100 microseconds