import pytest
from datetime import datetime

from hft_resource_monitor.metrics import (
    CacheMetrics, ContextSwitchInfo, InterruptInfo,
    NUMAStats, ThreadSchedulingInfo, LatencySpike
)


class TestCacheMetrics:
    """Test CacheMetrics data class"""
    
    def test_cache_metrics_creation(self):
        """Test creating cache metrics instance"""
        timestamp = datetime.now()
        metrics = CacheMetrics(
            timestamp=timestamp,
            l1_hits=1000, l1_misses=100,
            l2_hits=500, l2_misses=50,
            l3_hits=100, l3_misses=10,
            tlb_misses=5,
            false_sharing_events=2,
            cache_line_bounces=3
        )
        
        assert metrics.timestamp == timestamp
        assert metrics.l1_hits == 1000
        assert metrics.l1_misses == 100
        assert metrics.tlb_misses == 5
    
    def test_cache_hit_rates(self):
        """Test cache hit rate calculations"""
        metrics = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=900, l1_misses=100,  # 90% hit rate
            l2_hits=800, l2_misses=200,  # 80% hit rate
            l3_hits=700, l3_misses=300,  # 70% hit rate
            tlb_misses=0,
            false_sharing_events=0,
            cache_line_bounces=0
        )
        
        assert metrics.l1_hit_rate == 0.9
        assert metrics.l2_hit_rate == 0.8
        assert metrics.l3_hit_rate == 0.7
    
    def test_cache_hit_rates_zero_accesses(self):
        """Test cache hit rates with zero accesses"""
        metrics = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=0, l1_misses=0,
            l2_hits=0, l2_misses=0,
            l3_hits=0, l3_misses=0,
            tlb_misses=0,
            false_sharing_events=0,
            cache_line_bounces=0
        )
        
        assert metrics.l1_hit_rate == 0.0
        assert metrics.l2_hit_rate == 0.0
        assert metrics.l3_hit_rate == 0.0
    
    def test_cache_metrics_with_percentiles(self):
        """Test cache metrics with percentile data"""
        metrics = CacheMetrics(
            timestamp=datetime.now(),
            l1_hits=1000, l1_misses=100,
            l2_hits=500, l2_misses=50,
            l3_hits=100, l3_misses=10,
            tlb_misses=5,
            false_sharing_events=2,
            cache_line_bounces=3,
            percentiles={50: 0.9, 95: 0.95, 99: 0.99}
        )
        
        assert metrics.percentiles[50] == 0.9
        assert metrics.percentiles[95] == 0.95
        assert metrics.percentiles[99] == 0.99


class TestContextSwitchInfo:
    """Test ContextSwitchInfo data class"""
    
    def test_context_switch_creation(self):
        """Test creating context switch info"""
        timestamp = datetime.now()
        info = ContextSwitchInfo(
            timestamp=timestamp,
            pid=12345,
            tid=12346,
            cpu_from=0,
            cpu_to=1,
            voluntary=True,
            duration_us=15.5
        )
        
        assert info.timestamp == timestamp
        assert info.pid == 12345
        assert info.tid == 12346
        assert info.cpu_from == 0
        assert info.cpu_to == 1
        assert info.voluntary is True
        assert info.duration_us == 15.5
        assert info.stack_trace is None
    
    def test_context_switch_with_stack_trace(self):
        """Test context switch with stack trace"""
        info = ContextSwitchInfo(
            timestamp=datetime.now(),
            pid=12345,
            tid=12346,
            cpu_from=0,
            cpu_to=1,
            voluntary=False,
            duration_us=25.0,
            stack_trace=['func1', 'func2', 'func3'],
            preemption_reason='timer_interrupt'
        )
        
        assert info.voluntary is False
        assert len(info.stack_trace) == 3
        assert info.preemption_reason == 'timer_interrupt'


class TestInterruptInfo:
    """Test InterruptInfo data class"""
    
    def test_interrupt_info_creation(self):
        """Test creating interrupt info"""
        timestamp = datetime.now()
        info = InterruptInfo(
            timestamp=timestamp,
            cpu=0,
            irq_number=16,
            irq_type='hardware',
            duration_us=5.2,
            source='network_card'
        )
        
        assert info.timestamp == timestamp
        assert info.cpu == 0
        assert info.irq_number == 16
        assert info.irq_type == 'hardware'
        assert info.duration_us == 5.2
        assert info.source == 'network_card'
        assert info.coalesced_count == 1
    
    def test_interrupt_info_coalesced(self):
        """Test interrupt info with coalescing"""
        info = InterruptInfo(
            timestamp=datetime.now(),
            cpu=1,
            irq_number=0,
            irq_type='softirq',
            duration_us=10.0,
            source='timer',
            coalesced_count=5
        )
        
        assert info.irq_type == 'softirq'
        assert info.coalesced_count == 5


class TestNUMAStats:
    """Test NUMAStats data class"""
    
    def test_numa_stats_creation(self):
        """Test creating NUMA stats"""
        timestamp = datetime.now()
        hot_spots = [(0x1000, 100), (0x2000, 200)]
        
        stats = NUMAStats(
            timestamp=timestamp,
            node_id=0,
            local_accesses=10000,
            remote_accesses=1000,
            bandwidth_mb_per_sec=25000.5,
            hot_spots=hot_spots,
            inter_socket_overhead_us=2.5
        )
        
        assert stats.timestamp == timestamp
        assert stats.node_id == 0
        assert stats.local_accesses == 10000
        assert stats.remote_accesses == 1000
        assert stats.bandwidth_mb_per_sec == 25000.5
        assert len(stats.hot_spots) == 2
        assert stats.inter_socket_overhead_us == 2.5
    
    def test_numa_local_access_ratio(self):
        """Test NUMA local access ratio calculation"""
        stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=0,
            local_accesses=8000,
            remote_accesses=2000,
            bandwidth_mb_per_sec=20000,
            hot_spots=[],
            inter_socket_overhead_us=1.0
        )
        
        assert stats.local_access_ratio == 0.8
    
    def test_numa_with_heatmap(self):
        """Test NUMA stats with heatmap data"""
        heatmap_data = {
            'cache_lines': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        }
        
        stats = NUMAStats(
            timestamp=datetime.now(),
            node_id=1,
            local_accesses=5000,
            remote_accesses=5000,
            bandwidth_mb_per_sec=15000,
            hot_spots=[],
            inter_socket_overhead_us=3.0,
            heatmap=heatmap_data
        )
        
        assert stats.heatmap is not None
        assert 'cache_lines' in stats.heatmap
        assert len(stats.heatmap['cache_lines']) == 3


class TestThreadSchedulingInfo:
    """Test ThreadSchedulingInfo data class"""
    
    def test_thread_scheduling_creation(self):
        """Test creating thread scheduling info"""
        timestamp = datetime.now()
        info = ThreadSchedulingInfo(
            timestamp=timestamp,
            tid=12345,
            priority=20,
            nice_value=-5,
            scheduling_class='SCHED_FIFO',
            cpu_affinity=[0, 1, 2, 3],
            cpu_time_us=1000000.0,
            wait_time_us=50.0,
            priority_inversions=2,
            scheduling_jitter_us=5.5
        )
        
        assert info.timestamp == timestamp
        assert info.tid == 12345
        assert info.priority == 20
        assert info.nice_value == -5
        assert info.scheduling_class == 'SCHED_FIFO'
        assert len(info.cpu_affinity) == 4
        assert info.cpu_time_us == 1000000.0
        assert info.wait_time_us == 50.0
        assert info.priority_inversions == 2
        assert info.scheduling_jitter_us == 5.5


class TestLatencySpike:
    """Test LatencySpike data class"""
    
    def test_latency_spike_creation(self):
        """Test creating latency spike"""
        timestamp = datetime.now()
        details = {
            'cache_misses': 100,
            'context_switches': 5,
            'severity': 'high'
        }
        
        spike = LatencySpike(
            timestamp=timestamp,
            duration_us=150.0,
            thread_id=12345,
            cpu=2,
            cause='cache_thrashing',
            details=details
        )
        
        assert spike.timestamp == timestamp
        assert spike.duration_us == 150.0
        assert spike.thread_id == 12345
        assert spike.cpu == 2
        assert spike.cause == 'cache_thrashing'
        assert spike.details['severity'] == 'high'
        assert spike.stack_trace is None
    
    def test_latency_spike_with_context(self):
        """Test latency spike with additional context"""
        spike = LatencySpike(
            timestamp=datetime.now(),
            duration_us=200.0,
            thread_id=12346,
            cpu=3,
            cause='interrupt_storm',
            details={'irq_count': 1000},
            stack_trace=['func1', 'func2'],
            related_events=['IRQ 16 fired', 'Context switch occurred']
        )
        
        assert len(spike.stack_trace) == 2
        assert len(spike.related_events) == 2
        assert 'IRQ 16 fired' in spike.related_events