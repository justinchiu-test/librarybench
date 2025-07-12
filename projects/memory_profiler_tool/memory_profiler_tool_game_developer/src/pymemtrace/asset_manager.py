"""Asset memory manager for tracking game asset lifecycle and memory usage."""

import sys
import time
import weakref
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
import threading


class AssetType(Enum):
    """Types of game assets."""
    TEXTURE = "texture"
    SOUND = "sound"
    MODEL = "model"
    SHADER = "shader"
    ANIMATION = "animation"
    SCRIPT = "script"
    FONT = "font"
    LEVEL = "level"
    OTHER = "other"


class AssetState(Enum):
    """Lifecycle states of an asset."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    IN_USE = "in_use"
    CACHED = "cached"
    UNLOADING = "unloading"
    ERROR = "error"


@dataclass
class AssetInfo:
    """Information about a game asset."""
    asset_id: str
    asset_type: AssetType
    memory_size: int
    load_time: float
    last_used: float
    reference_count: int
    state: AssetState
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)


@dataclass
class AssetMemoryHeatmap:
    """Heatmap data for asset memory usage."""
    timestamp: float
    asset_groups: Dict[AssetType, int]
    total_memory: int
    hotspots: List[Tuple[str, int]]  # (asset_id, memory_size)


class AssetMemoryManager:
    """Manages and tracks memory usage of game assets."""
    
    def __init__(self):
        """Initialize the asset memory manager."""
        self.assets: Dict[str, AssetInfo] = {}
        self.asset_refs: Dict[str, weakref.ref] = {}
        self.orphaned_assets: Set[str] = set()
        self._lock = threading.Lock()
        self._heatmap_history: List[AssetMemoryHeatmap] = []
        self._leak_detection_enabled = True
        self._reference_tracking: Dict[str, List[str]] = defaultdict(list)
        
    def register_asset(self, asset_id: str, asset_type: AssetType, 
                      asset_object: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a new asset for tracking."""
        with self._lock:
            memory_size = sys.getsizeof(asset_object)
            
            asset_info = AssetInfo(
                asset_id=asset_id,
                asset_type=asset_type,
                memory_size=memory_size,
                load_time=time.time(),
                last_used=time.time(),
                reference_count=1,
                state=AssetState.LOADED,
                metadata=metadata or {}
            )
            
            self.assets[asset_id] = asset_info
            
            # Only create weak references for objects that support it
            try:
                self.asset_refs[asset_id] = weakref.ref(asset_object, 
                                                       lambda ref: self._on_asset_deleted(asset_id))
            except TypeError:
                # For objects that don't support weak references (like bytes), skip tracking
                pass
    
    def _on_asset_deleted(self, asset_id: str) -> None:
        """Called when an asset is garbage collected."""
        with self._lock:
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                if asset.reference_count > 0 and self._leak_detection_enabled:
                    self.orphaned_assets.add(asset_id)
                asset.state = AssetState.UNLOADED
    
    def update_asset_state(self, asset_id: str, new_state: AssetState) -> None:
        """Update the lifecycle state of an asset."""
        with self._lock:
            if asset_id in self.assets:
                self.assets[asset_id].state = new_state
                if new_state == AssetState.IN_USE:
                    self.assets[asset_id].last_used = time.time()
    
    def add_reference(self, asset_id: str, referencer_id: str) -> None:
        """Add a reference to an asset."""
        with self._lock:
            if asset_id in self.assets:
                self.assets[asset_id].reference_count += 1
                self._reference_tracking[asset_id].append(referencer_id)
    
    def remove_reference(self, asset_id: str, referencer_id: str) -> None:
        """Remove a reference from an asset."""
        with self._lock:
            if asset_id in self.assets:
                self.assets[asset_id].reference_count = max(0, 
                    self.assets[asset_id].reference_count - 1)
                if referencer_id in self._reference_tracking[asset_id]:
                    self._reference_tracking[asset_id].remove(referencer_id)
    
    def add_dependency(self, asset_id: str, dependency_id: str) -> None:
        """Add a dependency between assets."""
        with self._lock:
            if asset_id in self.assets:
                self.assets[asset_id].dependencies.add(dependency_id)
    
    def get_asset_info(self, asset_id: str) -> Optional[AssetInfo]:
        """Get information about a specific asset."""
        with self._lock:
            return self.assets.get(asset_id)
    
    def get_total_memory_by_type(self) -> Dict[AssetType, int]:
        """Get total memory usage grouped by asset type."""
        with self._lock:
            memory_by_type = defaultdict(int)
            for asset in self.assets.values():
                if asset.state in [AssetState.LOADED, AssetState.IN_USE, AssetState.CACHED]:
                    memory_by_type[asset.asset_type] += asset.memory_size
            return dict(memory_by_type)
    
    def get_memory_heatmap(self, top_n: int = 10) -> AssetMemoryHeatmap:
        """Generate a memory usage heatmap."""
        with self._lock:
            memory_by_type = self.get_total_memory_by_type()
            total_memory = sum(memory_by_type.values())
            
            # Find top memory consuming assets
            loaded_assets = [(a.asset_id, a.memory_size) 
                           for a in self.assets.values() 
                           if a.state in [AssetState.LOADED, AssetState.IN_USE, AssetState.CACHED]]
            hotspots = sorted(loaded_assets, key=lambda x: x[1], reverse=True)[:top_n]
            
            heatmap = AssetMemoryHeatmap(
                timestamp=time.time(),
                asset_groups=memory_by_type,
                total_memory=total_memory,
                hotspots=hotspots
            )
            
            self._heatmap_history.append(heatmap)
            return heatmap
    
    def detect_memory_leaks(self) -> List[str]:
        """Detect potential memory leaks in assets."""
        with self._lock:
            leaked_assets = []
            
            # Check for orphaned assets
            leaked_assets.extend(list(self.orphaned_assets))
            
            # Check for assets with references but no actual object
            for asset_id, ref in self.asset_refs.items():
                if ref() is None and asset_id in self.assets:
                    asset = self.assets[asset_id]
                    if asset.reference_count > 0:
                        leaked_assets.append(asset_id)
            
            # Check for circular dependencies
            for asset_id, asset in self.assets.items():
                if self._has_circular_dependency(asset_id, set()):
                    leaked_assets.append(asset_id)
            
            return list(set(leaked_assets))
    
    def _has_circular_dependency(self, asset_id: str, visited: Set[str]) -> bool:
        """Check if an asset has circular dependencies."""
        if asset_id in visited:
            return True
        
        visited.add(asset_id)
        
        if asset_id in self.assets:
            for dep_id in self.assets[asset_id].dependencies:
                if self._has_circular_dependency(dep_id, visited.copy()):
                    return True
        
        return False
    
    def get_unused_assets(self, threshold_seconds: float = 300) -> List[str]:
        """Get assets that haven't been used for a specified time."""
        with self._lock:
            current_time = time.time()
            unused = []
            
            for asset_id, asset in self.assets.items():
                if (asset.state == AssetState.LOADED and 
                    current_time - asset.last_used > threshold_seconds):
                    unused.append(asset_id)
            
            return unused
    
    def get_asset_lifecycle_stats(self) -> Dict[AssetState, int]:
        """Get count of assets in each lifecycle state."""
        with self._lock:
            stats = defaultdict(int)
            for asset in self.assets.values():
                stats[asset.state] += 1
            return dict(stats)
    
    def validate_references(self) -> Dict[str, List[str]]:
        """Validate all asset references and return invalid ones."""
        with self._lock:
            invalid_refs = {}
            
            for asset_id, asset in self.assets.items():
                invalid = []
                
                # Check if weak reference is still valid
                if asset_id in self.asset_refs:
                    if self.asset_refs[asset_id]() is None and asset.reference_count > 0:
                        invalid.append("weak_ref_dead")
                
                # Check reference count consistency
                tracked_refs = len(self._reference_tracking.get(asset_id, []))
                if tracked_refs != asset.reference_count:
                    invalid.append(f"ref_count_mismatch:{tracked_refs}!={asset.reference_count}")
                
                if invalid:
                    invalid_refs[asset_id] = invalid
            
            return invalid_refs
    
    def unload_asset(self, asset_id: str) -> bool:
        """Unload an asset from memory."""
        with self._lock:
            if asset_id not in self.assets:
                return False
            
            asset = self.assets[asset_id]
            if asset.reference_count > 0:
                return False
            
            asset.state = AssetState.UNLOADING
            if asset_id in self.asset_refs:
                del self.asset_refs[asset_id]
            
            asset.state = AssetState.UNLOADED
            return True
    
    def get_dependency_graph(self, asset_id: str) -> Dict[str, Set[str]]:
        """Get the dependency graph for an asset."""
        with self._lock:
            graph = {}
            visited = set()
            
            def build_graph(aid: str):
                if aid in visited or aid not in self.assets:
                    return
                
                visited.add(aid)
                deps = self.assets[aid].dependencies.copy()
                graph[aid] = deps
                
                for dep in deps:
                    build_graph(dep)
            
            build_graph(asset_id)
            return graph
    
    def calculate_total_memory(self, include_cached: bool = True) -> int:
        """Calculate total memory used by all assets."""
        with self._lock:
            total = 0
            states = [AssetState.LOADED, AssetState.IN_USE]
            if include_cached:
                states.append(AssetState.CACHED)
            
            for asset in self.assets.values():
                if asset.state in states:
                    total += asset.memory_size
            
            return total
    
    def clear_orphaned_assets(self) -> int:
        """Clear the list of orphaned assets and return count."""
        with self._lock:
            count = len(self.orphaned_assets)
            self.orphaned_assets.clear()
            return count