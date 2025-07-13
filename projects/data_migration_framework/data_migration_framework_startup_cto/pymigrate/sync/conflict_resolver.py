"""Conflict resolution for bi-directional synchronization."""

import importlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from pymigrate.models.config import ConflictResolutionStrategy
from pymigrate.models.data import DataChange, ConflictReport

logger = logging.getLogger(__name__)


@dataclass
class ResolutionResult:
    """Result of conflict resolution."""
    resolved: bool
    winning_change: Optional[DataChange] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class ConflictResolver:
    """Resolves conflicts during bi-directional synchronization."""
    
    def __init__(self, strategy: ConflictResolutionStrategy):
        """Initialize conflict resolver with strategy."""
        self.strategy = strategy
        self._custom_resolvers: Dict[str, Callable] = {}
        
    async def resolve(
        self,
        source_change: DataChange,
        target_change: DataChange,
        priority_rules: Optional[Dict[str, int]] = None
    ) -> ResolutionResult:
        """Resolve conflict between source and target changes."""
        if self.strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            return await self._resolve_last_write_wins(source_change, target_change)
            
        elif self.strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            return await self._resolve_priority_based(
                source_change, target_change, priority_rules
            )
            
        elif self.strategy == ConflictResolutionStrategy.CUSTOM:
            return await self._resolve_custom(source_change, target_change)
            
        elif self.strategy == ConflictResolutionStrategy.MANUAL:
            return await self._resolve_manual(source_change, target_change)
            
        else:
            raise ValueError(f"Unknown resolution strategy: {self.strategy}")
            
    async def _resolve_last_write_wins(
        self,
        source_change: DataChange,
        target_change: DataChange
    ) -> ResolutionResult:
        """Resolve using last-write-wins strategy."""
        # Compare timestamps
        if source_change.timestamp > target_change.timestamp:
            winner = source_change
            reason = "source_newer"
        else:
            winner = target_change
            reason = "target_newer"
            
        return ResolutionResult(
            resolved=True,
            winning_change=winner,
            details={
                "strategy": "last_write_wins",
                "reason": reason,
                "source_timestamp": source_change.timestamp.isoformat(),
                "target_timestamp": target_change.timestamp.isoformat(),
                "time_diff_seconds": abs(
                    (source_change.timestamp - target_change.timestamp).total_seconds()
                )
            }
        )
        
    async def _resolve_priority_based(
        self,
        source_change: DataChange,
        target_change: DataChange,
        priority_rules: Optional[Dict[str, int]] = None
    ) -> ResolutionResult:
        """Resolve using priority-based strategy."""
        if not priority_rules:
            # Default: source has higher priority
            priority_rules = {"source": 100, "target": 50}
            
        source_priority = priority_rules.get(source_change.source_system, 50)
        target_priority = priority_rules.get(target_change.source_system, 50)
        
        if source_priority > target_priority:
            winner = source_change
            reason = "source_higher_priority"
        elif target_priority > source_priority:
            winner = target_change
            reason = "target_higher_priority"
        else:
            # Equal priority, fall back to timestamp
            return await self._resolve_last_write_wins(source_change, target_change)
            
        return ResolutionResult(
            resolved=True,
            winning_change=winner,
            details={
                "strategy": "priority_based",
                "reason": reason,
                "source_priority": source_priority,
                "target_priority": target_priority,
                "priority_rules": priority_rules
            }
        )
        
    async def _resolve_custom(
        self,
        source_change: DataChange,
        target_change: DataChange
    ) -> ResolutionResult:
        """Resolve using custom resolver function."""
        table_name = source_change.table_name
        
        # Look for table-specific resolver
        if table_name in self._custom_resolvers:
            resolver = self._custom_resolvers[table_name]
        else:
            # Look for default resolver
            resolver = self._custom_resolvers.get("default")
            
        if not resolver:
            logger.warning(
                f"No custom resolver found for table {table_name}, "
                "falling back to last-write-wins"
            )
            return await self._resolve_last_write_wins(source_change, target_change)
            
        try:
            result = await resolver(source_change, target_change)
            return ResolutionResult(
                resolved=True,
                winning_change=result["winner"],
                details={
                    "strategy": "custom",
                    "resolver": resolver.__name__,
                    **result.get("details", {})
                }
            )
        except Exception as e:
            logger.error(f"Custom resolver failed: {e}")
            return ResolutionResult(
                resolved=False,
                details={
                    "strategy": "custom",
                    "error": str(e)
                }
            )
            
    async def _resolve_manual(
        self,
        source_change: DataChange,
        target_change: DataChange
    ) -> ResolutionResult:
        """Mark conflict for manual resolution."""
        return ResolutionResult(
            resolved=False,
            details={
                "strategy": "manual",
                "reason": "requires_manual_intervention",
                "source_data": source_change.data,
                "target_data": target_change.data,
                "differences": self._calculate_differences(
                    source_change.data, 
                    target_change.data
                )
            }
        )
        
    def register_custom_resolver(
        self,
        table_name: str,
        resolver: Callable
    ) -> None:
        """Register a custom resolver for a specific table."""
        self._custom_resolvers[table_name] = resolver
        logger.info(f"Registered custom resolver for table: {table_name}")
        
    def load_custom_resolver_module(self, module_path: str) -> None:
        """Load custom resolvers from a Python module."""
        try:
            module = importlib.import_module(module_path)
            
            # Look for resolver functions in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a resolver function
                if (
                    callable(attr) and 
                    hasattr(attr, "__resolver_table__")
                ):
                    table_name = getattr(attr, "__resolver_table__")
                    self.register_custom_resolver(table_name, attr)
                    
        except Exception as e:
            logger.error(f"Failed to load custom resolver module: {e}")
            raise
            
    def _calculate_differences(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate differences between source and target data."""
        differences = {}
        
        all_keys = set(source_data.keys()) | set(target_data.keys())
        
        for key in all_keys:
            source_val = source_data.get(key)
            target_val = target_data.get(key)
            
            if source_val != target_val:
                differences[key] = {
                    "source": source_val,
                    "target": target_val
                }
                
        return differences
        
    def get_resolution_stats(self) -> Dict[str, Any]:
        """Get statistics about conflict resolutions."""
        # In a real implementation, this would track resolution statistics
        return {
            "strategy": self.strategy.value,
            "custom_resolvers": list(self._custom_resolvers.keys()),
        }