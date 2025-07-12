"""Object pool analyzer for measuring pooling effectiveness in games."""

import gc
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Type, Callable
from collections import defaultdict, deque
import threading
import weakref


@dataclass
class PoolMetrics:
    """Metrics for a single object pool."""
    pool_name: str
    object_type: str
    pool_size: int
    active_objects: int
    recycled_objects: int
    total_allocations: int
    total_deallocations: int
    allocation_savings: int
    overflow_count: int
    utilization_rate: float
    gc_collections_saved: int
    memory_saved: int
    avg_object_lifetime: float


@dataclass 
class AllocationPattern:
    """Pattern of allocations for pool optimization."""
    timestamp: float
    allocation_rate: float  # allocations per second
    deallocation_rate: float
    peak_usage: int
    avg_usage: float
    pattern_duration: float


class ObjectPool:
    """A monitored object pool for game objects."""
    
    def __init__(self, object_type: Type, initial_size: int = 10, 
                 max_size: int = 100, name: Optional[str] = None):
        """
        Initialize an object pool.
        
        Args:
            object_type: Type of objects to pool
            initial_size: Initial pool size
            max_size: Maximum pool size
            name: Optional name for the pool
        """
        self.object_type = object_type
        self.name = name or object_type.__name__
        self.initial_size = initial_size
        self.max_size = max_size
        self._pool: deque = deque()
        self._active_objects: weakref.WeakSet = weakref.WeakSet()
        self._lock = threading.Lock()
        
        # Metrics
        self.total_allocations = 0
        self.total_deallocations = 0
        self.allocation_savings = 0
        self.overflow_count = 0
        self.gc_collections_before = 0
        self._allocation_times: deque = deque(maxlen=1000)
        self._object_lifetimes: deque = deque(maxlen=1000)
        self._last_gc_count = gc.get_count()
        
        # Pre-populate pool
        for _ in range(initial_size):
            self._pool.append(self._create_object())
    
    def _create_object(self) -> Any:
        """Create a new object for the pool."""
        return self.object_type()
    
    def acquire(self) -> Any:
        """Acquire an object from the pool."""
        with self._lock:
            self._allocation_times.append(time.time())
            
            if self._pool:
                obj = self._pool.pop()
                self.allocation_savings += 1
            else:
                obj = self._create_object()
                self.total_allocations += 1
                if len(self._active_objects) >= self.max_size:
                    self.overflow_count += 1
            
            self._active_objects.add(obj)
            return obj
    
    def release(self, obj: Any) -> None:
        """Release an object back to the pool."""
        with self._lock:
            if obj in self._active_objects:
                self._active_objects.discard(obj)
                self.total_deallocations += 1
                
                if len(self._pool) < self.max_size:
                    # Reset object state if it has a reset method
                    if hasattr(obj, 'reset'):
                        obj.reset()
                    self._pool.append(obj)
                
                # Track object lifetime
                if hasattr(obj, '_pool_acquired_time'):
                    lifetime = time.time() - obj._pool_acquired_time
                    self._object_lifetimes.append(lifetime)
    
    def get_metrics(self) -> PoolMetrics:
        """Get current pool metrics."""
        with self._lock:
            current_gc = gc.get_count()
            gc_saved = sum(current_gc[i] - self._last_gc_count[i] 
                          for i in range(len(current_gc)))
            
            utilization = len(self._active_objects) / self.max_size if self.max_size > 0 else 0
            avg_lifetime = (sum(self._object_lifetimes) / len(self._object_lifetimes) 
                           if self._object_lifetimes else 0)
            
            # Calculate memory saved
            obj_size = sys.getsizeof(self.object_type())
            memory_saved = self.allocation_savings * obj_size
            
            return PoolMetrics(
                pool_name=self.name,
                object_type=self.object_type.__name__,
                pool_size=len(self._pool),
                active_objects=len(self._active_objects),
                recycled_objects=len(self._pool),
                total_allocations=self.total_allocations,
                total_deallocations=self.total_deallocations,
                allocation_savings=self.allocation_savings,
                overflow_count=self.overflow_count,
                utilization_rate=utilization,
                gc_collections_saved=max(0, gc_saved),
                memory_saved=memory_saved,
                avg_object_lifetime=avg_lifetime
            )


class ObjectPoolAnalyzer:
    """Analyzes object pooling effectiveness in games."""
    
    def __init__(self):
        """Initialize the object pool analyzer."""
        self.pools: Dict[str, ObjectPool] = {}
        self._allocation_patterns: Dict[str, List[AllocationPattern]] = defaultdict(list)
        self._pattern_window = 60.0  # 60 second window for pattern analysis
        self._lock = threading.Lock()
        self._monitoring_enabled = False
        self._gc_baseline = gc.get_stats()
    
    def create_pool(self, object_type: Type, initial_size: int = 10,
                   max_size: int = 100, name: Optional[str] = None) -> ObjectPool:
        """Create and register a new object pool."""
        pool_name = name or object_type.__name__
        
        with self._lock:
            pool = ObjectPool(object_type, initial_size, max_size, pool_name)
            self.pools[pool_name] = pool
            return pool
    
    def get_pool(self, name: str) -> Optional[ObjectPool]:
        """Get a pool by name."""
        return self.pools.get(name)
    
    def analyze_efficiency(self, pool_name: str) -> Dict[str, float]:
        """Analyze the efficiency of a specific pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            return {}
        
        metrics = pool.get_metrics()
        
        # Calculate efficiency metrics
        allocation_reduction = (metrics.allocation_savings / 
                              (metrics.total_allocations + metrics.allocation_savings) 
                              if metrics.total_allocations + metrics.allocation_savings > 0 else 0)
        
        overflow_rate = (metrics.overflow_count / metrics.total_allocations 
                        if metrics.total_allocations > 0 else 0)
        
        gc_impact = metrics.gc_collections_saved / max(1, metrics.total_allocations)
        
        return {
            "allocation_reduction": allocation_reduction,
            "overflow_rate": overflow_rate,
            "utilization_efficiency": metrics.utilization_rate,
            "gc_impact_reduction": gc_impact,
            "memory_efficiency": metrics.memory_saved / max(1, metrics.total_allocations),
            "object_reuse_rate": metrics.allocation_savings / max(1, metrics.total_deallocations)
        }
    
    def record_allocation_pattern(self, pool_name: str) -> None:
        """Record allocation patterns for a pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            return
        
        with self._lock:
            current_time = time.time()
            
            # Calculate rates over the last pattern window
            recent_allocations = [t for t in pool._allocation_times 
                                if current_time - t <= self._pattern_window]
            
            if len(recent_allocations) >= 2:
                duration = recent_allocations[-1] - recent_allocations[0]
                alloc_rate = len(recent_allocations) / duration if duration > 0 else 0
                
                metrics = pool.get_metrics()
                pattern = AllocationPattern(
                    timestamp=current_time,
                    allocation_rate=alloc_rate,
                    deallocation_rate=metrics.total_deallocations / duration if duration > 0 else 0,
                    peak_usage=metrics.active_objects,
                    avg_usage=metrics.utilization_rate * pool.max_size,
                    pattern_duration=duration
                )
                
                self._allocation_patterns[pool_name].append(pattern)
    
    def suggest_pool_size(self, pool_name: str) -> Dict[str, int]:
        """Suggest optimal pool size based on usage patterns."""
        patterns = self._allocation_patterns.get(pool_name, [])
        if not patterns:
            return {"suggested_size": 10, "reason": "no_data"}
        
        # Analyze recent patterns
        recent_patterns = patterns[-10:]  # Last 10 pattern windows
        
        peak_usages = [p.peak_usage for p in recent_patterns]
        avg_usages = [p.avg_usage for p in recent_patterns]
        allocation_rates = [p.allocation_rate for p in recent_patterns]
        
        # Calculate suggestions
        avg_peak = sum(peak_usages) / len(peak_usages)
        max_peak = max(peak_usages)
        avg_rate = sum(allocation_rates) / len(allocation_rates)
        
        # Suggest size based on peaks with buffer
        suggested_size = int(max_peak * 1.2)  # 20% buffer
        
        # Adjust based on allocation rate
        if avg_rate > 100:  # High allocation rate
            suggested_size = int(suggested_size * 1.5)
        
        return {
            "suggested_size": suggested_size,
            "current_size": self.pools[pool_name].max_size,
            "avg_peak_usage": avg_peak,
            "max_peak_usage": max_peak,
            "avg_allocation_rate": avg_rate,
            "reason": "pattern_analysis"
        }
    
    def measure_gc_impact(self) -> Dict[str, Any]:
        """Measure the impact of pooling on garbage collection."""
        current_gc_stats = gc.get_stats()
        
        # Compare with baseline
        gc_reduction = {
            "collections_saved": 0,
            "time_saved_ms": 0,
            "objects_saved": 0
        }
        
        # Calculate total savings across all pools
        total_allocations_saved = sum(pool.allocation_savings for pool in self.pools.values())
        total_memory_saved = sum(pool.get_metrics().memory_saved for pool in self.pools.values())
        
        # Estimate GC impact
        avg_gc_time = 5.0  # Average GC time in ms (conservative estimate)
        collections_prevented = total_allocations_saved // 1000  # Rough estimate
        
        return {
            "total_allocations_saved": total_allocations_saved,
            "total_memory_saved": total_memory_saved,
            "estimated_gc_collections_prevented": collections_prevented,
            "estimated_time_saved_ms": collections_prevented * avg_gc_time,
            "pools_analyzed": len(self.pools)
        }
    
    def get_all_metrics(self) -> Dict[str, PoolMetrics]:
        """Get metrics for all pools."""
        return {name: pool.get_metrics() for name, pool in self.pools.items()}
    
    def optimize_all_pools(self) -> Dict[str, Dict[str, int]]:
        """Optimize all pool sizes based on usage patterns."""
        optimizations = {}
        
        for pool_name in self.pools:
            self.record_allocation_pattern(pool_name)
            optimizations[pool_name] = self.suggest_pool_size(pool_name)
        
        return optimizations
    
    def get_pool_comparison(self) -> List[Dict[str, Any]]:
        """Compare efficiency across all pools."""
        comparisons = []
        
        for pool_name, pool in self.pools.items():
            metrics = pool.get_metrics()
            efficiency = self.analyze_efficiency(pool_name)
            
            comparisons.append({
                "pool_name": pool_name,
                "utilization": metrics.utilization_rate,
                "allocation_reduction": efficiency.get("allocation_reduction", 0),
                "memory_saved": metrics.memory_saved,
                "overflow_rate": efficiency.get("overflow_rate", 0),
                "effectiveness_score": (
                    efficiency.get("allocation_reduction", 0) * 0.4 +
                    (1 - efficiency.get("overflow_rate", 0)) * 0.3 +
                    efficiency.get("utilization_efficiency", 0) * 0.3
                )
            })
        
        return sorted(comparisons, key=lambda x: x["effectiveness_score"], reverse=True)
    
    def reset_metrics(self, pool_name: Optional[str] = None) -> None:
        """Reset metrics for a specific pool or all pools."""
        with self._lock:
            if pool_name:
                if pool_name in self.pools:
                    pool = self.pools[pool_name]
                    pool.total_allocations = 0
                    pool.total_deallocations = 0
                    pool.allocation_savings = 0
                    pool.overflow_count = 0
            else:
                for pool in self.pools.values():
                    pool.total_allocations = 0
                    pool.total_deallocations = 0
                    pool.allocation_savings = 0
                    pool.overflow_count = 0