import pytest
import time
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from hft_resource_monitor import HFTResourceMonitor
from hft_resource_monitor.exceptions import (
    ConfigurationError, PermissionError, ProcessNotFoundError
)
from hft_resource_monitor.metrics import CacheMetrics


class TestHFTResourceMonitor:
    """Test suite for HFTResourceMonitor core functionality"""
    
    def test_monitor_initialization(self):
        """Test monitor initializes with default values"""
        monitor = HFTResourceMonitor()
        assert monitor.sampling_interval_us == 100
        assert monitor.cpu_affinity == []
        assert monitor.realtime_priority == 0
        assert not monitor.monitoring_active
        assert len(monitor.attached_processes) == 0
    
    def test_configure_valid_parameters(self):
        """Test configuration with valid parameters"""
        monitor = HFTResourceMonitor()
        
        # Test without realtime priority (or with 0) to avoid permission issues
        monitor.configure(
            sampling_interval_us=200,
            cpu_affinity=[0, 1],
            realtime_priority=0  # Use 0 to avoid permission issues
        )
        assert monitor.sampling_interval_us == 200
        assert monitor.cpu_affinity == [0, 1]
        assert monitor.realtime_priority == 0
        
        # Test with non-zero priority only if running as root
        import os
        if os.geteuid() == 0:
            monitor.configure(realtime_priority=50)
            assert monitor.realtime_priority == 50
    
    def test_configure_invalid_sampling_interval(self):
        """Test configuration rejects too small sampling interval"""
        monitor = HFTResourceMonitor()
        with pytest.raises(ConfigurationError, match="at least 10 microseconds"):
            monitor.configure(sampling_interval_us=5)
    
    def test_configure_invalid_priority(self):
        """Test configuration rejects invalid priority values"""
        monitor = HFTResourceMonitor()
        with pytest.raises(ConfigurationError, match="between 0 and 99"):
            monitor.configure(realtime_priority=-1)
        with pytest.raises(ConfigurationError, match="between 0 and 99"):
            monitor.configure(realtime_priority=100)
    
    @patch('psutil.Process')
    def test_attach_process_success(self, mock_process_class):
        """Test successful process attachment"""
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process_class.return_value = mock_process
        
        monitor = HFTResourceMonitor()
        monitor.attach_process(12345)
        
        assert 12345 in monitor.attached_processes
        assert monitor.attached_processes[12345] == mock_process
        mock_process_class.assert_called_once_with(12345)
    
    @patch('psutil.Process')
    def test_attach_process_not_running(self, mock_process_class):
        """Test attaching to non-running process raises error"""
        mock_process = Mock()
        mock_process.is_running.return_value = False
        mock_process_class.return_value = mock_process
        
        monitor = HFTResourceMonitor()
        with pytest.raises(ProcessNotFoundError, match="not running"):
            monitor.attach_process(12345)
    
    @patch('psutil.Process')
    def test_attach_process_not_found(self, mock_process_class):
        """Test attaching to non-existent process raises error"""
        import psutil
        mock_process_class.side_effect = psutil.NoSuchProcess(12345)
        
        monitor = HFTResourceMonitor()
        with pytest.raises(ProcessNotFoundError, match="not found"):
            monitor.attach_process(12345)
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        monitor = HFTResourceMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor.monitoring_active
        assert monitor._monitor_thread is not None
        assert monitor._monitor_thread.is_alive()
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor.monitoring_active
        time.sleep(0.1)  # Give thread time to stop
        assert not monitor._monitor_thread.is_alive()
    
    def test_start_monitoring_idempotent(self):
        """Test that starting monitoring twice is safe"""
        monitor = HFTResourceMonitor()
        monitor.start_monitoring()
        thread1 = monitor._monitor_thread
        
        # Starting again should not create new thread
        monitor.start_monitoring()
        assert monitor._monitor_thread == thread1
        
        monitor.stop_monitoring()
    
    @patch('psutil.Process')
    def test_monitoring_collects_metrics(self, mock_process_class):
        """Test that monitoring loop collects metrics"""
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process.num_ctx_switches.return_value = Mock(voluntary=10, involuntary=5)
        mock_process.threads.return_value = [Mock(id=1, user_time=1.0)]
        mock_process.nice.return_value = 0
        mock_process.cpu_affinity.return_value = [0, 1]
        mock_process_class.return_value = mock_process
        
        monitor = HFTResourceMonitor()
        monitor.configure(sampling_interval_us=100)
        monitor.attach_process(12345)
        
        # Clear existing metrics
        monitor._cache_metrics.clear()
        
        monitor.start_monitoring()
        time.sleep(0.5)  # Let it collect some metrics
        monitor.stop_monitoring()
        
        # Should have collected cache metrics
        assert len(monitor._cache_metrics) > 0
        
        # Verify cache metrics structure
        metric = monitor._cache_metrics[0]
        assert isinstance(metric, CacheMetrics)
        assert metric.l1_hits >= 0
        assert metric.l1_misses >= 0
        assert 0 <= metric.l1_hit_rate <= 1
    
    def test_get_cache_metrics_time_window(self):
        """Test retrieving cache metrics within time window"""
        monitor = HFTResourceMonitor()
        
        # Add some test metrics
        now = datetime.now()
        old_metric = CacheMetrics(
            timestamp=now - timedelta(milliseconds=2),
            l1_hits=1000, l1_misses=10,
            l2_hits=500, l2_misses=5,
            l3_hits=100, l3_misses=1,
            tlb_misses=0, false_sharing_events=0, cache_line_bounces=0
        )
        recent_metric = CacheMetrics(
            timestamp=now,
            l1_hits=2000, l1_misses=20,
            l2_hits=1000, l2_misses=10,
            l3_hits=200, l3_misses=2,
            tlb_misses=0, false_sharing_events=0, cache_line_bounces=0
        )
        
        monitor._cache_metrics.append(old_metric)
        monitor._cache_metrics.append(recent_metric)
        
        # Get metrics from last 1ms
        metrics = monitor.get_cache_metrics(time_window_us=1000)
        assert len(metrics) == 1
        assert metrics[0] == recent_metric
        
        # Get metrics from last 3ms (should include both)
        metrics = monitor.get_cache_metrics(time_window_us=3000)
        assert len(metrics) == 2
    
    def test_get_cache_metrics_percentiles(self):
        """Test cache metrics percentile calculation"""
        monitor = HFTResourceMonitor()
        
        # Add multiple metrics
        now = datetime.now()
        for i in range(10):
            metric = CacheMetrics(
                timestamp=now,
                l1_hits=900 + i * 10,  # 900, 910, 920, ..., 990
                l1_misses=100 - i * 10,  # 100, 90, 80, ..., 10
                l2_hits=100, l2_misses=10,
                l3_hits=50, l3_misses=5,
                tlb_misses=0, false_sharing_events=0, cache_line_bounces=0
            )
            monitor._cache_metrics.append(metric)
        
        metrics = monitor.get_cache_metrics(
            time_window_us=10000,
            percentiles=[50, 95, 99]
        )
        
        # Should have percentiles on last metric
        assert metrics[-1].percentiles is not None
        assert 50 in metrics[-1].percentiles
        assert 95 in metrics[-1].percentiles
        assert 99 in metrics[-1].percentiles
    
    def test_context_switch_filtering(self):
        """Test context switch filtering by duration"""
        monitor = HFTResourceMonitor()
        
        # Add test context switches with different durations
        from hft_resource_monitor.metrics import ContextSwitchInfo
        
        now = datetime.now()
        short_switch = ContextSwitchInfo(
            timestamp=now, pid=1, tid=1,
            cpu_from=0, cpu_to=1,
            voluntary=True, duration_us=5.0
        )
        long_switch = ContextSwitchInfo(
            timestamp=now, pid=1, tid=1,
            cpu_from=1, cpu_to=0,
            voluntary=False, duration_us=15.0
        )
        
        monitor._context_switches.append(short_switch)
        monitor._context_switches.append(long_switch)
        
        # Get all switches
        all_switches = monitor.get_context_switches()
        assert len(all_switches) == 2
        
        # Get only long switches
        long_switches = monitor.get_context_switches(min_duration_us=10)
        assert len(long_switches) == 1
        assert long_switches[0] == long_switch
    
    def test_numa_stats_local_access_ratio(self):
        """Test NUMA stats local access ratio calculation"""
        from hft_resource_monitor.metrics import NUMAStats
        
        stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=0,
            local_accesses=9000,
            remote_accesses=1000,
            bandwidth_mb_per_sec=10000,
            hot_spots=[],
            inter_socket_overhead_us=2.0
        )
        
        assert stats.local_access_ratio == 0.9
        
        # Test zero accesses
        empty_stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=0,
            local_accesses=0,
            remote_accesses=0,
            bandwidth_mb_per_sec=0,
            hot_spots=[],
            inter_socket_overhead_us=0
        )
        assert empty_stats.local_access_ratio == 0.0
    
    def test_latency_spike_detection(self):
        """Test latency spike detection and filtering"""
        monitor = HFTResourceMonitor()
        
        # Add test latency spikes
        from hft_resource_monitor.metrics import LatencySpike
        
        now = datetime.now()
        small_spike = LatencySpike(
            timestamp=now,
            duration_us=30.0,
            thread_id=1,
            cpu=0,
            cause='cache_miss',
            details={'severity': 'low'}
        )
        large_spike = LatencySpike(
            timestamp=now,
            duration_us=75.0,
            thread_id=1,
            cpu=1,
            cause='context_switch',
            details={'severity': 'high'}
        )
        
        monitor._latency_spikes.append(small_spike)
        monitor._latency_spikes.append(large_spike)
        
        # Get all spikes
        all_spikes = monitor.detect_latency_spikes(threshold_us=0)
        assert len(all_spikes) == 2
        
        # Get only large spikes
        large_spikes = monitor.detect_latency_spikes(threshold_us=50)
        assert len(large_spikes) == 1
        assert large_spikes[0] == large_spike
        
        # Test cause analysis
        analyzed_spikes = monitor.detect_latency_spikes(
            threshold_us=0,
            include_cause_analysis=True
        )
        assert all(spike.related_events is not None for spike in analyzed_spikes)
        assert len(analyzed_spikes[0].related_events) > 0