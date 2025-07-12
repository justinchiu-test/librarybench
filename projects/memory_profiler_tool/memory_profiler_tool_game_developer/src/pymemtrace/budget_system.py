"""Memory budget system for enforcing memory limits in games."""

import time
import heapq
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set, Tuple
from collections import defaultdict
import threading


class EvictionStrategy(Enum):
    """Asset eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    PRIORITY = "priority"  # Priority-based
    SIZE = "size"  # Largest first
    AGE = "age"  # Oldest first
    HYBRID = "hybrid"  # Combination of factors


class BudgetViolationType(Enum):
    """Types of budget violations."""
    WARNING = "warning"  # Approaching limit
    EXCEEDED = "exceeded"  # Over limit
    CRITICAL = "critical"  # Severely over limit


@dataclass
class MemoryBudget:
    """Memory budget configuration."""
    name: str
    max_bytes: int
    warning_threshold: float = 0.8  # Warn at 80% usage
    critical_threshold: float = 0.95  # Critical at 95% usage
    parent: Optional[str] = None
    priority: int = 0


@dataclass
class BudgetViolation:
    """Information about a budget violation."""
    budget_name: str
    violation_type: BudgetViolationType
    current_usage: int
    budget_limit: int
    timestamp: float
    message: str


@dataclass
class EvictableAsset:
    """Asset that can be evicted."""
    asset_id: str
    size: int
    last_used: float
    use_count: int
    priority: int
    age: float
    subsystem: str
    
    def __lt__(self, other):
        """For priority queue comparison."""
        return self.priority < other.priority


class MemoryBudgetSystem:
    """Manages memory budgets and automatic asset eviction."""
    
    def __init__(self):
        """Initialize the memory budget system."""
        self.budgets: Dict[str, MemoryBudget] = {}
        self.usage: Dict[str, int] = defaultdict(int)
        self.assets: Dict[str, EvictableAsset] = {}
        self.asset_to_budget: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._violation_callbacks: List[Callable[[BudgetViolation], None]] = []
        self._eviction_callbacks: List[Callable[[str, str], None]] = []  # asset_id, reason
        self._eviction_strategy = EvictionStrategy.HYBRID
        self._auto_evict_enabled = True
    
    def create_budget(self, name: str, max_bytes: int, 
                     warning_threshold: float = 0.8,
                     critical_threshold: float = 0.95,
                     parent: Optional[str] = None,
                     priority: int = 0) -> None:
        """Create a new memory budget."""
        with self._lock:
            budget = MemoryBudget(
                name=name,
                max_bytes=max_bytes,
                warning_threshold=warning_threshold,
                critical_threshold=critical_threshold,
                parent=parent,
                priority=priority
            )
            self.budgets[name] = budget
            self.usage[name] = 0
    
    def register_asset(self, asset_id: str, budget_name: str, size: int,
                      priority: int = 0, subsystem: str = "default") -> None:
        """Register an asset with a budget."""
        with self._lock:
            if budget_name not in self.budgets:
                raise ValueError(f"Budget '{budget_name}' does not exist")
            
            asset = EvictableAsset(
                asset_id=asset_id,
                size=size,
                last_used=time.time(),
                use_count=1,
                priority=priority,
                age=time.time(),
                subsystem=subsystem
            )
            
            self.assets[asset_id] = asset
            self.asset_to_budget[asset_id] = budget_name
            self._update_usage(budget_name, size)
            
            # Check for violations after adding
            self._check_budget_violations(budget_name)
    
    def unregister_asset(self, asset_id: str) -> None:
        """Unregister an asset from its budget."""
        with self._lock:
            if asset_id not in self.assets:
                return
            
            asset = self.assets[asset_id]
            budget_name = self.asset_to_budget[asset_id]
            
            self._update_usage(budget_name, -asset.size)
            del self.assets[asset_id]
            del self.asset_to_budget[asset_id]
    
    def update_asset_usage(self, asset_id: str) -> None:
        """Update asset usage statistics."""
        with self._lock:
            if asset_id in self.assets:
                self.assets[asset_id].last_used = time.time()
                self.assets[asset_id].use_count += 1
    
    def _update_usage(self, budget_name: str, delta: int) -> None:
        """Update usage for a budget and its parents."""
        self.usage[budget_name] += delta
        
        # Update parent budgets
        budget = self.budgets.get(budget_name)
        if budget and budget.parent:
            self._update_usage(budget.parent, delta)
    
    def _check_budget_violations(self, budget_name: str) -> List[BudgetViolation]:
        """Check for budget violations."""
        violations = []
        
        if budget_name not in self.budgets:
            return violations
        
        budget = self.budgets[budget_name]
        current_usage = self.usage[budget_name]
        usage_ratio = current_usage / budget.max_bytes if budget.max_bytes > 0 else 0
        
        violation = None
        
        if usage_ratio >= 1.0:
            violation = BudgetViolation(
                budget_name=budget_name,
                violation_type=BudgetViolationType.EXCEEDED,
                current_usage=current_usage,
                budget_limit=budget.max_bytes,
                timestamp=time.time(),
                message=f"Budget '{budget_name}' exceeded: {current_usage}/{budget.max_bytes} bytes"
            )
        elif usage_ratio >= budget.critical_threshold:
            violation = BudgetViolation(
                budget_name=budget_name,
                violation_type=BudgetViolationType.CRITICAL,
                current_usage=current_usage,
                budget_limit=budget.max_bytes,
                timestamp=time.time(),
                message=f"Budget '{budget_name}' critical: {usage_ratio:.1%} used"
            )
        elif usage_ratio >= budget.warning_threshold:
            violation = BudgetViolation(
                budget_name=budget_name,
                violation_type=BudgetViolationType.WARNING,
                current_usage=current_usage,
                budget_limit=budget.max_bytes,
                timestamp=time.time(),
                message=f"Budget '{budget_name}' warning: {usage_ratio:.1%} used"
            )
        
        if violation:
            violations.append(violation)
            for callback in self._violation_callbacks:
                callback(violation)
            
            # Auto-evict if enabled and exceeded
            if (self._auto_evict_enabled and 
                violation.violation_type == BudgetViolationType.EXCEEDED):
                self._auto_evict(budget_name)
        
        return violations
    
    def _calculate_eviction_score(self, asset: EvictableAsset) -> float:
        """Calculate eviction score based on strategy."""
        current_time = time.time()
        
        if self._eviction_strategy == EvictionStrategy.LRU:
            return current_time - asset.last_used
        elif self._eviction_strategy == EvictionStrategy.LFU:
            return 1.0 / (asset.use_count + 1)
        elif self._eviction_strategy == EvictionStrategy.PRIORITY:
            return -asset.priority
        elif self._eviction_strategy == EvictionStrategy.SIZE:
            return asset.size
        elif self._eviction_strategy == EvictionStrategy.AGE:
            return current_time - asset.age
        elif self._eviction_strategy == EvictionStrategy.HYBRID:
            # Combine multiple factors
            lru_score = (current_time - asset.last_used) / 3600  # Hours
            lfu_score = 1.0 / (asset.use_count + 1)
            size_score = asset.size / (1024 * 1024)  # MB
            priority_score = (100 - asset.priority) / 100
            
            return lru_score * 0.3 + lfu_score * 0.2 + size_score * 0.3 + priority_score * 0.2
        
        return 0.0
    
    def _auto_evict(self, budget_name: str) -> List[str]:
        """Automatically evict assets to meet budget."""
        budget = self.budgets[budget_name]
        target_usage = int(budget.max_bytes * 0.7)  # Target 70% usage
        current_usage = self.usage[budget_name]
        
        if current_usage <= target_usage:
            return []
        
        # Find evictable assets for this budget
        evictable = []
        for asset_id, asset in self.assets.items():
            if self.asset_to_budget[asset_id] == budget_name:
                score = self._calculate_eviction_score(asset)
                evictable.append((score, asset_id))
        
        # Sort by eviction score (higher score = more likely to evict)
        evictable.sort(reverse=True)
        
        evicted = []
        bytes_to_free = current_usage - target_usage
        bytes_freed = 0
        
        for score, asset_id in evictable:
            if bytes_freed >= bytes_to_free:
                break
            
            asset = self.assets[asset_id]
            self.unregister_asset(asset_id)
            evicted.append(asset_id)
            bytes_freed += asset.size
            
            # Notify callbacks
            for callback in self._eviction_callbacks:
                callback(asset_id, f"auto_eviction_{self._eviction_strategy.value}")
        
        return evicted
    
    def set_eviction_strategy(self, strategy: EvictionStrategy) -> None:
        """Set the eviction strategy."""
        with self._lock:
            self._eviction_strategy = strategy
    
    def enable_auto_eviction(self, enabled: bool) -> None:
        """Enable or disable automatic eviction."""
        with self._lock:
            self._auto_evict_enabled = enabled
    
    def add_violation_callback(self, callback: Callable[[BudgetViolation], None]) -> None:
        """Add a callback for budget violations."""
        self._violation_callbacks.append(callback)
    
    def add_eviction_callback(self, callback: Callable[[str, str], None]) -> None:
        """Add a callback for asset evictions."""
        self._eviction_callbacks.append(callback)
    
    def get_budget_status(self, budget_name: str) -> Dict[str, Any]:
        """Get status of a specific budget."""
        with self._lock:
            if budget_name not in self.budgets:
                return {}
            
            budget = self.budgets[budget_name]
            usage = self.usage[budget_name]
            usage_ratio = usage / budget.max_bytes if budget.max_bytes > 0 else 0
            
            # Count assets in this budget
            asset_count = sum(1 for b in self.asset_to_budget.values() if b == budget_name)
            
            return {
                "name": budget_name,
                "usage": usage,
                "limit": budget.max_bytes,
                "usage_percentage": usage_ratio * 100,
                "asset_count": asset_count,
                "warning_threshold": budget.warning_threshold * 100,
                "critical_threshold": budget.critical_threshold * 100,
                "is_warning": usage_ratio >= budget.warning_threshold,
                "is_critical": usage_ratio >= budget.critical_threshold,
                "is_exceeded": usage_ratio >= 1.0
            }
    
    def get_hierarchy_status(self) -> Dict[str, Any]:
        """Get status of the entire budget hierarchy."""
        with self._lock:
            hierarchy = {}
            
            # Build hierarchy
            for name, budget in self.budgets.items():
                status = self.get_budget_status(name)
                
                if budget.parent:
                    if budget.parent not in hierarchy:
                        hierarchy[budget.parent] = {"children": {}}
                    hierarchy[budget.parent]["children"][name] = status
                else:
                    if name not in hierarchy:
                        hierarchy[name] = status
                    else:
                        hierarchy[name].update(status)
            
            return hierarchy
    
    def suggest_evictions(self, budget_name: str, bytes_needed: int) -> List[Tuple[str, int]]:
        """Suggest assets to evict to free up space."""
        with self._lock:
            suggestions = []
            
            # Find evictable assets
            evictable = []
            for asset_id, asset in self.assets.items():
                if self.asset_to_budget[asset_id] == budget_name:
                    score = self._calculate_eviction_score(asset)
                    evictable.append((score, asset_id, asset.size))
            
            evictable.sort(reverse=True)
            
            bytes_suggested = 0
            for score, asset_id, size in evictable:
                if bytes_suggested >= bytes_needed:
                    break
                suggestions.append((asset_id, size))
                bytes_suggested += size
            
            return suggestions
    
    def get_budget_analytics(self) -> Dict[str, Any]:
        """Get analytics for all budgets."""
        with self._lock:
            total_allocated = sum(b.max_bytes for b in self.budgets.values())
            total_used = sum(self.usage.values())
            
            analytics = {
                "total_budgets": len(self.budgets),
                "total_allocated": total_allocated,
                "total_used": total_used,
                "overall_usage_percentage": (total_used / total_allocated * 100) if total_allocated > 0 else 0,
                "budgets_over_warning": sum(1 for b in self.budgets 
                                           if self.usage[b] / self.budgets[b].max_bytes >= self.budgets[b].warning_threshold),
                "budgets_exceeded": sum(1 for b in self.budgets 
                                      if self.usage[b] >= self.budgets[b].max_bytes),
                "total_assets": len(self.assets),
                "eviction_strategy": self._eviction_strategy.value,
                "auto_eviction_enabled": self._auto_evict_enabled
            }
            
            return analytics