import pytest
import time
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import psutil

from hft_resource_monitor import HFTResourceMonitor
from hft_resource_monitor.exceptions import (
    ConfigurationError, PermissionError, ProcessNotFoundError,
    HardwareNotSupportedError
)
from hft_resource_monitor.metrics import (
    CacheMetrics, ContextSwitchInfo, InterruptInfo,
    NUMAStats, ThreadSchedulingInfo, LatencySpike
)


class TestEdgeCases:
    """Edge case tests for HFT Resource Monitor"""
    
    def test_zero_sampling_interval_rejection(self):
        """Test that zero sampling interval is rejected"""
        monitor = HFTResourceMonitor()
        with pytest.raises(ConfigurationError):
            monitor.configure(sampling_interval_us=0)
    
    def test_negative_sampling_interval_rejection(self):
        """Test that negative sampling interval is rejected"""
        monitor = HFTResourceMonitor()
        with pytest.raises(ConfigurationError):
            monitor.configure(sampling_interval_us=-100)
    
    def test_extremely_high_sampling_interval(self):
        """Test extremely high sampling interval"""
        monitor = HFTResourceMonitor()
        monitor.configure(sampling_interval_us=10_000_000)  # 10 seconds
        assert monitor.sampling_interval_us == 10_000_000
    
    def test_attach_pid_zero(self):
        """Test attaching to PID 0 (kernel)"""
        monitor = HFTResourceMonitor()
        with pytest.raises(ProcessNotFoundError):
            monitor.attach_process(0)
    
    def test_attach_negative_pid(self):
        """Test attaching to negative PID"""
        monitor = HFTResourceMonitor()
        with pytest.raises((ProcessNotFoundError, ValueError)):
            monitor.attach_process(-1)
    
    def test_attach_max_pid(self):
        """Test attaching to maximum PID value"""
        monitor = HFTResourceMonitor()
        max_pid = 2**31 - 1  # Max PID on most systems
        with pytest.raises(ProcessNotFoundError):
            monitor.attach_process(max_pid)
    
    def test_empty_cpu_affinity_list(self):
        """Test configuration with empty CPU affinity list"""
        monitor = HFTResourceMonitor()
        monitor.configure(cpu_affinity=[])
        assert monitor.cpu_affinity == []
    
    def test_invalid_cpu_affinity_ignored(self):
        """Test invalid CPU numbers in affinity are handled"""
        monitor = HFTResourceMonitor()
        # Configure with potentially invalid CPU numbers
        monitor.configure(cpu_affinity=[0, 1, 999])
        assert monitor.cpu_affinity == [0, 1, 999]  # Stored but may fail later
    
    def test_all_zero_cache_metrics(self):
        """Test cache metrics with all zero values"""
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=0, l1_misses=0,
            l2_hits=0, l2_misses=0,
            l3_hits=0, l3_misses=0,
            tlb_misses=0,
            false_sharing_events=0,
            cache_line_bounces=0
        )
        
        assert metric.l1_hit_rate == 0.0
        assert metric.l2_hit_rate == 0.0
        assert metric.l3_hit_rate == 0.0
    
    def test_maximum_cache_values(self):
        """Test cache metrics with maximum values"""
        max_val = 2**63 - 1  # Max signed 64-bit int
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=max_val, l1_misses=1,
            l2_hits=max_val, l2_misses=1,
            l3_hits=max_val, l3_misses=1,
            tlb_misses=max_val,
            false_sharing_events=max_val,
            cache_line_bounces=max_val
        )
        
        # Should handle large numbers
        assert metric.l1_hit_rate > 0.99999
    
    def test_context_switch_same_cpu(self):
        """Test context switch on same CPU"""
        switch = ContextSwitchInfo(
            timestamp=datetime.now(),
            pid=12345, tid=12346,
            cpu_from=0, cpu_to=0,  # Same CPU
            voluntary=True,
            duration_us=5.0
        )
        
        assert switch.cpu_from == switch.cpu_to
    
    def test_context_switch_zero_duration(self):
        """Test context switch with zero duration"""
        switch = ContextSwitchInfo(
            timestamp=datetime.now(),
            pid=12345, tid=12346,
            cpu_from=0, cpu_to=1,
            voluntary=False,
            duration_us=0.0
        )
        
        assert switch.duration_us == 0.0
    
    def test_numa_single_node_system(self):
        """Test NUMA stats on single-node system"""
        stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=0,
            local_accesses=1000000,
            remote_accesses=0,  # No remote on single node
            bandwidth_mb_per_sec=50000,
            hot_spots=[],
            inter_socket_overhead_us=0.0
        )
        
        assert stats.local_access_ratio == 1.0
    
    def test_thread_negative_nice_value(self):
        """Test thread with negative nice value (higher priority)"""
        info = ThreadSchedulingInfo(
            timestamp=datetime.now(),
            tid=12345,
            priority=10,
            nice_value=-20,  # Highest priority
            scheduling_class='SCHED_OTHER',
            cpu_affinity=[0],
            cpu_time_us=1000.0,
            wait_time_us=0.0,
            priority_inversions=0,
            scheduling_jitter_us=0.1
        )
        
        assert info.nice_value == -20
    
    def test_latency_spike_zero_duration_filtered(self):
        """Test that zero-duration spikes are filtered"""
        monitor = HFTResourceMonitor()
        
        # Add spike with zero duration
        spike = LatencySpike(
            timestamp=datetime.now(),
            duration_us=0.0,
            thread_id=12345,
            cpu=0,
            cause='none',
            details={}
        )
        monitor._latency_spikes.append(spike)
        
        # Should be filtered out with any threshold
        spikes = monitor.detect_latency_spikes(threshold_us=0.001)
        assert len(spikes) == 0
    
    def test_monitor_without_attached_processes(self):
        """Test monitoring with no attached processes"""
        monitor = HFTResourceMonitor()
        monitor.start_monitoring()
        time.sleep(0.1)
        monitor.stop_monitoring()
        
        # Should not crash, metrics should be empty
        assert len(monitor.get_cache_metrics()) == 0
    
    def test_time_window_future_time(self):
        """Test time window extending into future"""
        monitor = HFTResourceMonitor()
        
        # Add metric with current time
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=1000, l1_misses=100,
            l2_hits=500, l2_misses=50,
            l3_hits=100, l3_misses=10,
            tlb_misses=0, false_sharing_events=0,
            cache_line_bounces=0
        )
        monitor._cache_metrics.append(metric)
        
        # Request metrics from future window (should include current)
        metrics = monitor.get_cache_metrics(time_window_us=10_000_000)  # 10 seconds
        assert len(metrics) == 1
    
    def test_percentile_empty_list(self):
        """Test percentile calculation with empty metrics"""
        monitor = HFTResourceMonitor()
        metrics = monitor.get_cache_metrics(percentiles=[50, 95])
        assert len(metrics) == 0
    
    def test_percentile_single_value(self):
        """Test percentile with single metric value"""
        monitor = HFTResourceMonitor()
        
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=1000, l1_misses=0,
            l2_hits=0, l2_misses=0,
            l3_hits=0, l3_misses=0,
            tlb_misses=0, false_sharing_events=0,
            cache_line_bounces=0
        )
        monitor._cache_metrics.append(metric)
        
        metrics = monitor.get_cache_metrics(percentiles=[25, 50, 75])
        # All percentiles should be same value
        assert metrics[0].percentiles[25] == 1.0
        assert metrics[0].percentiles[50] == 1.0
        assert metrics[0].percentiles[75] == 1.0
    
    def test_interrupt_coalescing_overflow(self):
        """Test interrupt with very high coalescing count"""
        info = InterruptInfo(
            timestamp=datetime.now(),
            cpu=0,
            irq_number=255,
            irq_type='hardware',
            duration_us=1000.0,
            source='network',
            coalesced_count=1_000_000
        )
        
        assert info.coalesced_count == 1_000_000
    
    @patch('os.cpu_count', return_value=None)
    def test_unknown_cpu_count(self, mock_cpu_count):
        """Test behavior when CPU count is unknown"""
        monitor = HFTResourceMonitor()
        # Should handle None cpu_count gracefully
        monitor._detect_latency_spikes(12345, datetime.now())
    
    @patch('psutil.Process')
    def test_zombie_process_handling(self, mock_process_class):
        """Test handling of zombie processes"""
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process.status.return_value = 'zombie'
        mock_process_class.return_value = mock_process
        
        monitor = HFTResourceMonitor()
        monitor.attach_process(12345)
        
        # Should handle zombie state
        assert 12345 in monitor.attached_processes
    
    def test_numa_empty_hot_spots(self):
        """Test NUMA stats with no hot spots"""
        stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=0,
            local_accesses=1000,
            remote_accesses=100,
            bandwidth_mb_per_sec=10000,
            hot_spots=[],  # Empty
            inter_socket_overhead_us=1.0
        )
        
        assert len(stats.hot_spots) == 0
    
    def test_thread_scheduling_rt_priority_limits(self):
        """Test thread scheduling with RT priority limits"""
        # SCHED_FIFO with max priority
        info = ThreadSchedulingInfo(
            timestamp=datetime.now(),
            tid=12345,
            priority=99,  # Max RT priority
            nice_value=0,  # Ignored for RT
            scheduling_class='SCHED_FIFO',
            cpu_affinity=[0],
            cpu_time_us=1000.0,
            wait_time_us=0.0,
            priority_inversions=0,
            scheduling_jitter_us=0.01
        )
        
        assert info.priority == 99
        assert info.scheduling_class == 'SCHED_FIFO'
    
    def test_cache_line_boundary_values(self):
        """Test cache metrics at cache line boundaries"""
        # 64-byte cache line typical
        metric = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=64, l1_misses=64,
            l2_hits=64, l2_misses=64,
            l3_hits=64, l3_misses=64,
            tlb_misses=64,
            false_sharing_events=1,
            cache_line_bounces=1
        )
        
        assert metric.l1_hit_rate == 0.5
        assert metric.l2_hit_rate == 0.5
        assert metric.l3_hit_rate == 0.5
    
    def test_microsecond_precision_boundary(self):
        """Test microsecond precision at boundaries"""
        monitor = HFTResourceMonitor()
        
        # Test minimum microsecond values
        switch = ContextSwitchInfo(
            timestamp=datetime.now(),
            pid=12345, tid=12346,
            cpu_from=0, cpu_to=1,
            voluntary=True,
            duration_us=0.001  # 1 nanosecond
        )
        monitor._context_switches.append(switch)
        
        switches = monitor.get_context_switches(min_duration_us=0.0005)
        assert len(switches) == 1
    
    def test_deque_thread_safety_limits(self):
        """Test deque behavior at capacity limits"""
        monitor = HFTResourceMonitor()
        
        # Fill to exactly maxlen
        for i in range(10000):
            monitor._cache_metrics.append(CacheMetrics(
                timestamp=datetime.now(),
                l1_hits=i, l1_misses=0,
                l2_hits=0, l2_misses=0,
                l3_hits=0, l3_misses=0,
                tlb_misses=0, false_sharing_events=0,
                cache_line_bounces=0
            ))
        
        assert len(monitor._cache_metrics) == 10000
        
        # Add one more
        monitor._cache_metrics.append(CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=10000, l1_misses=0,
            l2_hits=0, l2_misses=0,
            l3_hits=0, l3_misses=0,
            tlb_misses=0, false_sharing_events=0,
            cache_line_bounces=0
        ))
        
        # Should still be at maxlen
        assert len(monitor._cache_metrics) == 10000
        # First item should be dropped
        assert monitor._cache_metrics[0].l1_hits == 1