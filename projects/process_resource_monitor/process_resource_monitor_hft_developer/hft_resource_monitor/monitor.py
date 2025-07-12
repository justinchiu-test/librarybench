import os
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from collections import deque, defaultdict
from datetime import datetime
import psutil
import numpy as np

from .metrics import (
    CacheMetrics, ContextSwitchInfo, InterruptInfo, 
    NUMAStats, ThreadSchedulingInfo, LatencySpike
)
from .exceptions import (
    ConfigurationError, PermissionError, ProcessNotFoundError,
    HardwareNotSupportedError
)


class HFTResourceMonitor:
    """High-frequency trading process resource monitor with microsecond precision"""
    
    def __init__(self):
        self.sampling_interval_us: int = 100
        self.cpu_affinity: List[int] = []
        self.realtime_priority: int = 0
        self.attached_processes: Dict[int, psutil.Process] = {}
        self.monitoring_active: bool = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Metric storage with circular buffers for efficiency
        self._cache_metrics: deque = deque(maxlen=10000)
        self._context_switches: deque = deque(maxlen=10000)
        self._interrupts: deque = deque(maxlen=10000)
        self._numa_stats: deque = deque(maxlen=1000)
        self._thread_scheduling: deque = deque(maxlen=10000)
        self._latency_spikes: deque = deque(maxlen=1000)
        
        # Performance counters simulation (in real implementation would use perf_events)
        self._perf_counters = defaultdict(lambda: defaultdict(int))
        self._last_check_time = time.perf_counter()
        
    def configure(self, sampling_interval_us: int = 100, 
                  cpu_affinity: Optional[List[int]] = None,
                  realtime_priority: int = 0) -> None:
        """Configure monitoring parameters"""
        if sampling_interval_us < 10:
            raise ConfigurationError("Sampling interval must be at least 10 microseconds")
        if realtime_priority < 0 or realtime_priority > 99:
            raise ConfigurationError("Realtime priority must be between 0 and 99")
            
        self.sampling_interval_us = sampling_interval_us
        self.cpu_affinity = cpu_affinity or []
        self.realtime_priority = realtime_priority
        
        # Check permissions for realtime scheduling
        if realtime_priority > 0 and os.geteuid() != 0:
            try:
                import resource
                soft, hard = resource.getrlimit(resource.RLIMIT_RTPRIO)
                if realtime_priority > hard:
                    raise PermissionError(
                        f"Realtime priority {realtime_priority} exceeds limit {hard}"
                    )
            except ImportError:
                pass
    
    def attach_process(self, pid: int, track_cache: bool = True, 
                      track_numa: bool = True) -> None:
        """Attach to a process for monitoring"""
        try:
            process = psutil.Process(pid)
            if not process.is_running():
                raise ProcessNotFoundError(f"Process {pid} is not running")
                
            self.attached_processes[pid] = process
            
            # Initialize performance counters for this process
            self._perf_counters[pid] = {
                'cache': {'l1_hits': 0, 'l1_misses': 0, 'l2_hits': 0, 
                         'l2_misses': 0, 'l3_hits': 0, 'l3_misses': 0},
                'context_switches': {'voluntary': 0, 'involuntary': 0},
                'numa': {'local_accesses': 0, 'remote_accesses': 0}
            }
            
        except psutil.NoSuchProcess:
            raise ProcessNotFoundError(f"Process with PID {pid} not found")
    
    def start_monitoring(self) -> None:
        """Start the monitoring thread"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="HFTMonitor",
            daemon=True
        )
        
        # Set CPU affinity if specified
        if self.cpu_affinity:
            try:
                import os
                os.sched_setaffinity(self._monitor_thread.ident, self.cpu_affinity)
            except Exception:
                pass
                
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring thread"""
        if not self.monitoring_active:
            return
            
        self.monitoring_active = False
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in separate thread"""
        interval_seconds = self.sampling_interval_us / 1_000_000
        
        while not self._stop_event.is_set():
            start_time = time.perf_counter()
            
            # Collect metrics for all attached processes
            for pid, process in list(self.attached_processes.items()):
                try:
                    if process.is_running():
                        self._collect_metrics(pid, process)
                except psutil.NoSuchProcess:
                    del self.attached_processes[pid]
            
            # Sleep for remainder of interval
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0, interval_seconds - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _collect_metrics(self, pid: int, process: psutil.Process) -> None:
        """Collect all metrics for a process"""
        timestamp = datetime.now()
        
        try:
            # Simulate cache metrics (in real implementation would read from perf counters)
            self._collect_cache_metrics(pid, timestamp)
            
            # Collect context switch info
            self._collect_context_switches(pid, process, timestamp)
            
            # Simulate NUMA stats
            self._collect_numa_stats(pid, timestamp)
            
            # Collect thread scheduling info
            self._collect_thread_scheduling(pid, process, timestamp)
            
            # Detect latency spikes
            self._detect_latency_spikes(pid, timestamp)
        except psutil.NoSuchProcess:
            # Process terminated, remove it
            if pid in self.attached_processes:
                del self.attached_processes[pid]
    
    def _collect_cache_metrics(self, pid: int, timestamp: datetime) -> None:
        """Simulate cache metric collection"""
        # In real implementation, would read from hardware performance counters
        counters = self._perf_counters[pid]['cache']
        
        # Simulate some cache activity
        counters['l1_hits'] += np.random.poisson(10000)
        counters['l1_misses'] += np.random.poisson(100)
        counters['l2_hits'] += np.random.poisson(1000)
        counters['l2_misses'] += np.random.poisson(50)
        counters['l3_hits'] += np.random.poisson(500)
        counters['l3_misses'] += np.random.poisson(10)
        
        metrics = CacheMetrics(
            timestamp=timestamp,
            l1_hits=counters['l1_hits'],
            l1_misses=counters['l1_misses'],
            l2_hits=counters['l2_hits'],
            l2_misses=counters['l2_misses'],
            l3_hits=counters['l3_hits'],
            l3_misses=counters['l3_misses'],
            tlb_misses=np.random.poisson(5),
            false_sharing_events=np.random.poisson(1),
            cache_line_bounces=np.random.poisson(2)
        )
        
        self._cache_metrics.append(metrics)
    
    def _collect_context_switches(self, pid: int, process: psutil.Process, 
                                 timestamp: datetime) -> None:
        """Collect context switch information"""
        try:
            ctx_switches = process.num_ctx_switches()
            counters = self._perf_counters[pid]['context_switches']
            
            # Calculate new switches since last check
            voluntary_new = ctx_switches.voluntary - counters.get('voluntary', 0)
            involuntary_new = ctx_switches.involuntary - counters.get('involuntary', 0)
            
            counters['voluntary'] = ctx_switches.voluntary
            counters['involuntary'] = ctx_switches.involuntary
            
            # Create context switch events
            for _ in range(voluntary_new):
                info = ContextSwitchInfo(
                    timestamp=timestamp,
                    pid=pid,
                    tid=pid,  # Simplified, would get actual thread ID
                    cpu_from=np.random.randint(0, os.cpu_count()),
                    cpu_to=np.random.randint(0, os.cpu_count()),
                    voluntary=True,
                    duration_us=np.random.exponential(5.0)  # Simulated duration
                )
                self._context_switches.append(info)
                
        except Exception:
            pass
    
    def _collect_numa_stats(self, pid: int, timestamp: datetime) -> None:
        """Simulate NUMA statistics collection"""
        # In real implementation would use numactl or read from /proc
        for node_id in range(2):  # Assume 2 NUMA nodes
            stats = NUMAStats(
                timestamp=timestamp,
                node_id=node_id,
                local_accesses=np.random.poisson(100000),
                remote_accesses=np.random.poisson(10000),
                bandwidth_mb_per_sec=np.random.uniform(10000, 50000),
                hot_spots=[(np.random.randint(0, 2**32), np.random.poisson(1000)) 
                          for _ in range(5)],
                inter_socket_overhead_us=np.random.exponential(2.0)
            )
            self._numa_stats.append(stats)
    
    def _collect_thread_scheduling(self, pid: int, process: psutil.Process,
                                  timestamp: datetime) -> None:
        """Collect thread scheduling information"""
        try:
            threads = process.threads()
            for thread in threads:
                info = ThreadSchedulingInfo(
                    timestamp=timestamp,
                    tid=thread.id,
                    priority=process.nice(),
                    nice_value=process.nice(),
                    scheduling_class='SCHED_OTHER',  # Simplified
                    cpu_affinity=list(process.cpu_affinity()),
                    cpu_time_us=thread.user_time * 1_000_000,
                    wait_time_us=np.random.exponential(10.0),
                    priority_inversions=np.random.poisson(0.1),
                    scheduling_jitter_us=np.random.exponential(1.0)
                )
                self._thread_scheduling.append(info)
        except Exception:
            pass
    
    def _detect_latency_spikes(self, pid: int, timestamp: datetime) -> None:
        """Detect and record latency spikes"""
        # Simulate occasional latency spikes
        if np.random.random() < 0.01:  # 1% chance of spike
            spike = LatencySpike(
                timestamp=timestamp,
                duration_us=np.random.exponential(100.0),
                thread_id=pid,
                cpu=np.random.randint(0, os.cpu_count()),
                cause=np.random.choice(['context_switch', 'cache_miss', 'interrupt']),
                details={'severity': 'high', 'impact': 'trading_latency'}
            )
            self._latency_spikes.append(spike)
    
    def get_cache_metrics(self, time_window_us: int = 1000,
                         percentiles: Optional[List[float]] = None) -> List[CacheMetrics]:
        """Get cache metrics within time window"""
        current_time = datetime.now()
        window_start = current_time.timestamp() - (time_window_us / 1_000_000)
        
        metrics = [m for m in self._cache_metrics 
                  if m.timestamp.timestamp() >= window_start]
        
        # Calculate percentiles if requested
        if metrics and percentiles is not None:
            # Use default percentiles if none specified but not explicitly None
            if percentiles == []:
                # Empty list means no percentiles
                pass
            else:
                if not percentiles:
                    percentiles = [50, 95, 99, 99.9]
                # Collect all hit rates
                l1_rates = [m.l1_hit_rate for m in metrics]
                if l1_rates:
                    percentile_values = np.percentile(l1_rates, percentiles)
                    # Add percentiles to last metric
                    metrics[-1].percentiles = dict(zip(percentiles, percentile_values))
        elif metrics and percentiles is None:
            # Default behavior when percentiles not specified
            percentiles = [50, 95, 99, 99.9]
            l1_rates = [m.l1_hit_rate for m in metrics]
            if l1_rates:
                percentile_values = np.percentile(l1_rates, percentiles)
                metrics[-1].percentiles = dict(zip(percentiles, percentile_values))
                
        return metrics
    
    def get_context_switches(self, include_stack_trace: bool = False,
                           min_duration_us: float = 0) -> List[ContextSwitchInfo]:
        """Get context switch information"""
        switches = [cs for cs in self._context_switches 
                   if cs.duration_us >= min_duration_us]
        
        if include_stack_trace:
            # In real implementation would capture stack traces
            for switch in switches:
                switch.stack_trace = ['simulated', 'stack', 'trace']
                
        return switches
    
    def get_numa_stats(self, include_heatmap: bool = False,
                      resolution: str = "cache_line") -> List[NUMAStats]:
        """Get NUMA statistics"""
        stats = list(self._numa_stats)
        
        if include_heatmap:
            # Generate simple heatmap
            for stat in stats:
                stat.heatmap = {
                    'data': [[np.random.randint(0, 100) for _ in range(10)] 
                            for _ in range(10)]
                }
                
        return stats
    
    def detect_latency_spikes(self, threshold_us: float = 50,
                            include_cause_analysis: bool = True) -> List[LatencySpike]:
        """Detect and analyze latency spikes"""
        spikes = [s for s in self._latency_spikes if s.duration_us >= threshold_us]
        
        if include_cause_analysis:
            # Add detailed cause analysis
            for spike in spikes:
                spike.related_events = [
                    f"Context switch at {spike.timestamp}",
                    f"Cache miss burst detected"
                ]
                
        return spikes
    
    def get_thread_scheduling_info(self, pid: Optional[int] = None) -> List[ThreadSchedulingInfo]:
        """Get thread scheduling information"""
        if pid is not None:
            return [t for t in self._thread_scheduling if t.tid == pid]
        return list(self._thread_scheduling)