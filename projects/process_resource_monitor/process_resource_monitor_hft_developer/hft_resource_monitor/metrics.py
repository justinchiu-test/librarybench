from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class CacheMetrics:
    """CPU cache performance metrics"""
    timestamp: datetime
    l1_hits: int
    l1_misses: int
    l2_hits: int
    l2_misses: int
    l3_hits: int
    l3_misses: int
    tlb_misses: int
    false_sharing_events: int
    cache_line_bounces: int
    percentiles: Optional[Dict[float, float]] = None
    
    @property
    def l1_hit_rate(self) -> float:
        total = self.l1_hits + self.l1_misses
        return self.l1_hits / total if total > 0 else 0.0
    
    @property
    def l2_hit_rate(self) -> float:
        total = self.l2_hits + self.l2_misses
        return self.l2_hits / total if total > 0 else 0.0
    
    @property
    def l3_hit_rate(self) -> float:
        total = self.l3_hits + self.l3_misses
        return self.l3_hits / total if total > 0 else 0.0


@dataclass
class ContextSwitchInfo:
    """Context switch event information"""
    timestamp: datetime
    pid: int
    tid: int
    cpu_from: int
    cpu_to: int
    voluntary: bool
    duration_us: float
    stack_trace: Optional[List[str]] = None
    preemption_reason: Optional[str] = None


@dataclass
class InterruptInfo:
    """Interrupt and softirq information"""
    timestamp: datetime
    cpu: int
    irq_number: int
    irq_type: str  # 'hardware' or 'softirq'
    duration_us: float
    source: str
    coalesced_count: int = 1


@dataclass
class NUMAStats:
    """NUMA memory access statistics"""
    timestamp: datetime
    node_id: int
    local_accesses: int
    remote_accesses: int
    bandwidth_mb_per_sec: float
    hot_spots: List[Tuple[int, int]]  # (address, access_count)
    inter_socket_overhead_us: float
    heatmap: Optional[Dict[str, List[List[int]]]] = None
    
    @property
    def local_access_ratio(self) -> float:
        total = self.local_accesses + self.remote_accesses
        return self.local_accesses / total if total > 0 else 0.0


@dataclass
class ThreadSchedulingInfo:
    """Thread scheduling and priority information"""
    timestamp: datetime
    tid: int
    priority: int
    nice_value: int
    scheduling_class: str  # 'SCHED_FIFO', 'SCHED_RR', 'SCHED_OTHER'
    cpu_affinity: List[int]
    cpu_time_us: float
    wait_time_us: float
    priority_inversions: int
    scheduling_jitter_us: float


@dataclass
class LatencySpike:
    """Latency spike detection result"""
    timestamp: datetime
    duration_us: float
    thread_id: int
    cpu: int
    cause: str
    details: Dict[str, any]
    stack_trace: Optional[List[str]] = None
    related_events: Optional[List[str]] = None