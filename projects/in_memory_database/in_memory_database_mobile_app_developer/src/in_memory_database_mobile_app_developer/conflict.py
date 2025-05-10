"""Conflict resolution strategies for MobileSyncDB."""

import copy
import logging
from enum import Enum
from typing import Dict, Any, List, Callable, Optional, Union, Set, Tuple

from .database import Record
from .exceptions import ConflictError


logger = logging.getLogger(__name__)


class ConflictStrategy(Enum):
    """Available conflict resolution strategies."""

    LAST_WRITE_WINS = "last_write_wins"
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MANUAL = "manual"
    CLIENT_PRIORITY = "client_priority"
    MERGE = "merge"


class ConflictRecord:
    """Represents a conflict between two versions of a record."""

    def __init__(
        self,
        record_id: str,
        server_record: Record,
        client_record: Record,
        field_conflicts: Set[str],
        table_name: str,
    ):
        """Initialize a conflict record."""
        self.record_id = record_id
        self.server_record = server_record
        self.client_record = client_record
        self.field_conflicts = field_conflicts
        self.table_name = table_name
        self.resolved_record: Optional[Record] = None
        self.resolution_strategy: Optional[str] = None
        self.resolution_time: Optional[float] = None
        self.resolved_by: Optional[str] = None

    def get_differences(self) -> Dict[str, Dict[str, Any]]:
        """Get the differences between the server and client records."""
        differences = {}
        
        # Identify all fields in either record
        all_fields = set(self.server_record.data.keys()) | set(self.client_record.data.keys())
        
        for field in all_fields:
            server_value = self.server_record.data.get(field)
            client_value = self.client_record.data.get(field)
            
            if server_value != client_value:
                differences[field] = {
                    "server": server_value,
                    "client": client_value,
                }
        
        return differences

    def to_dict(self) -> Dict[str, Any]:
        """Convert the conflict record to a dictionary."""
        return {
            "record_id": self.record_id,
            "table_name": self.table_name,
            "server_version": self.server_record.version,
            "client_version": self.client_record.version,
            "server_updated_at": self.server_record.updated_at,
            "client_updated_at": self.client_record.updated_at,
            "differences": self.get_differences(),
            "resolved": self.resolved_record is not None,
            "resolution_strategy": self.resolution_strategy,
            "resolution_time": self.resolution_time,
            "resolved_by": self.resolved_by,
        }


class MergeResult:
    """Result of a merge operation."""

    def __init__(
        self,
        success: bool,
        merged_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        unresolved_fields: Optional[List[str]] = None,
    ):
        """Initialize a merge result."""
        self.success = success
        self.merged_data = merged_data
        self.error = error
        self.unresolved_fields = unresolved_fields or []


class FieldMergeStrategy:
    """Strategy for merging individual fields during conflict resolution."""

    def __init__(
        self,
        field_name: str,
        strategy: Union[str, Callable[[Any, Any], Any]],
        description: Optional[str] = None,
    ):
        """Initialize a field merge strategy."""
        self.field_name = field_name
        self.strategy = strategy
        self.description = description or (
            f"Custom merge for {field_name}" 
            if callable(strategy) else 
            f"{strategy} for {field_name}"
        )

    def apply(self, server_value: Any, client_value: Any) -> Any:
        """Apply the merge strategy to resolve a conflict."""
        if self.strategy == "server_wins":
            return server_value
        elif self.strategy == "client_wins":
            return client_value
        elif self.strategy == "newer_wins":
            # This needs context about which is newer, handled by the resolver
            raise ValueError("newer_wins strategy requires context and should be handled by ConflictResolver")
        elif callable(self.strategy):
            return self.strategy(server_value, client_value)
        else:
            raise ValueError(f"Unknown field merge strategy: {self.strategy}")


class ConflictResolver:
    """Resolves conflicts between client and server records."""

    def __init__(self, default_strategy: str = ConflictStrategy.LAST_WRITE_WINS.value):
        """Initialize a conflict resolver with a default strategy."""
        self.default_strategy = default_strategy
        self.field_strategies: Dict[str, Dict[str, FieldMergeStrategy]] = {}
        self.client_priorities: Dict[str, int] = {}
        self.custom_resolvers: Dict[str, Callable] = {}
        self.notification_handler: Optional[Callable] = None

    def set_field_strategy(
        self,
        table_name: str,
        field_name: str,
        strategy: Union[str, Callable[[Any, Any], Any]],
        description: Optional[str] = None,
    ) -> None:
        """Set a merge strategy for a specific field in a table."""
        if table_name not in self.field_strategies:
            self.field_strategies[table_name] = {}
        
        self.field_strategies[table_name][field_name] = FieldMergeStrategy(
            field_name=field_name,
            strategy=strategy,
            description=description,
        )

    def set_table_strategy(
        self,
        table_name: str,
        strategy: str,
    ) -> None:
        """Set the default strategy for an entire table."""
        if strategy not in [s.value for s in ConflictStrategy]:
            valid_strategies = ", ".join([s.value for s in ConflictStrategy])
            raise ValueError(f"Invalid conflict strategy: {strategy}. Valid strategies: {valid_strategies}")
        
        # Store this as a special field strategy that applies to the whole table
        if table_name not in self.field_strategies:
            self.field_strategies[table_name] = {}
        
        self.field_strategies[table_name]["__table__"] = FieldMergeStrategy(
            field_name="__table__",
            strategy=strategy,
            description=f"Table-wide strategy: {strategy}",
        )

    def set_client_priority(self, client_id: str, priority: int) -> None:
        """Set the priority for a client for client priority resolution."""
        self.client_priorities[client_id] = priority

    def register_custom_resolver(
        self,
        table_name: str,
        resolver: Callable[[ConflictRecord], MergeResult],
    ) -> None:
        """Register a custom conflict resolver for a table."""
        self.custom_resolvers[table_name] = resolver

    def set_notification_handler(
        self,
        handler: Callable[[ConflictRecord], None],
    ) -> None:
        """Set a handler for conflict notifications."""
        self.notification_handler = handler

    def _get_strategy_for_field(
        self,
        table_name: str,
        field_name: str,
    ) -> Union[str, Callable, None]:
        """Get the merge strategy for a specific field."""
        # Check for field-specific strategy
        if (
            table_name in self.field_strategies and
            field_name in self.field_strategies[table_name]
        ):
            return self.field_strategies[table_name][field_name].strategy
        
        # Check for table-wide strategy
        if (
            table_name in self.field_strategies and
            "__table__" in self.field_strategies[table_name]
        ):
            return self.field_strategies[table_name]["__table__"].strategy
        
        # Fall back to default strategy
        return self.default_strategy

    def _notify_conflict(self, conflict: ConflictRecord) -> None:
        """Notify about a conflict if a handler is registered."""
        if self.notification_handler:
            try:
                self.notification_handler(conflict)
            except Exception as e:
                logger.error(f"Error in conflict notification handler: {str(e)}")

    def _apply_server_wins(self, conflict: ConflictRecord) -> Record:
        """Apply server wins resolution strategy."""
        return copy.deepcopy(conflict.server_record)

    def _apply_client_wins(self, conflict: ConflictRecord) -> Record:
        """Apply client wins resolution strategy."""
        return copy.deepcopy(conflict.client_record)

    def _apply_last_write_wins(self, conflict: ConflictRecord) -> Record:
        """Apply last-write-wins resolution strategy."""
        if conflict.server_record.updated_at >= conflict.client_record.updated_at:
            return copy.deepcopy(conflict.server_record)
        else:
            return copy.deepcopy(conflict.client_record)

    def _apply_client_priority(self, conflict: ConflictRecord) -> Record:
        """Apply client priority resolution strategy."""
        client_id = conflict.client_record.client_id
        server_client_id = conflict.server_record.client_id
        
        if client_id is None:
            return copy.deepcopy(conflict.server_record)
        
        if server_client_id is None:
            return copy.deepcopy(conflict.client_record)
        
        client_priority = self.client_priorities.get(client_id, 0)
        server_client_priority = self.client_priorities.get(server_client_id, 0)
        
        if client_priority >= server_client_priority:
            return copy.deepcopy(conflict.client_record)
        else:
            return copy.deepcopy(conflict.server_record)

    def _apply_merge(self, conflict: ConflictRecord) -> MergeResult:
        """Apply merge resolution strategy."""
        merged_data = {}
        unresolved_fields = []
        
        # Get all fields from both records
        all_fields = set(conflict.server_record.data.keys()) | set(conflict.client_record.data.keys())
        
        for field in all_fields:
            server_value = conflict.server_record.data.get(field)
            client_value = conflict.client_record.data.get(field)
            
            # If the values are the same, no conflict
            if server_value == client_value:
                merged_data[field] = server_value
                continue
            
            # Get strategy for this field
            strategy = self._get_strategy_for_field(conflict.table_name, field)
            
            try:
                if strategy == "server_wins" or strategy == ConflictStrategy.SERVER_WINS.value:
                    merged_data[field] = server_value
                elif strategy == "client_wins" or strategy == ConflictStrategy.CLIENT_WINS.value:
                    merged_data[field] = client_value
                elif strategy == "last_write_wins" or strategy == ConflictStrategy.LAST_WRITE_WINS.value:
                    if conflict.server_record.updated_at >= conflict.client_record.updated_at:
                        merged_data[field] = server_value
                    else:
                        merged_data[field] = client_value
                elif strategy == "client_priority" or strategy == ConflictStrategy.CLIENT_PRIORITY.value:
                    client_id = conflict.client_record.client_id
                    server_client_id = conflict.server_record.client_id
                    
                    if client_id is None:
                        merged_data[field] = server_value
                    elif server_client_id is None:
                        merged_data[field] = client_value
                    else:
                        client_priority = self.client_priorities.get(client_id, 0)
                        server_client_priority = self.client_priorities.get(server_client_id, 0)
                        
                        if client_priority >= server_client_priority:
                            merged_data[field] = client_value
                        else:
                            merged_data[field] = server_value
                elif strategy == "manual" or strategy == ConflictStrategy.MANUAL.value:
                    # Can't resolve automatically
                    unresolved_fields.append(field)
                elif callable(strategy):
                    # Use custom field merge function
                    merged_data[field] = strategy(server_value, client_value)
                else:
                    logger.warning(f"Unknown merge strategy for field {field}: {strategy}")
                    unresolved_fields.append(field)
            except Exception as e:
                logger.error(f"Error merging field {field}: {str(e)}")
                unresolved_fields.append(field)
        
        if unresolved_fields:
            return MergeResult(
                success=False,
                merged_data=merged_data,
                unresolved_fields=unresolved_fields,
                error="Some fields could not be automatically resolved",
            )
        
        return MergeResult(
            success=True,
            merged_data=merged_data,
        )

    def resolve(
        self,
        conflict: ConflictRecord,
        strategy: Optional[str] = None,
    ) -> Optional[Record]:
        """Resolve a conflict using the specified or default strategy."""
        # If already resolved, return the resolved record
        if conflict.resolved_record:
            return conflict.resolved_record
        
        # Determine strategy to use
        strategy = strategy or self.default_strategy
        
        try:
            # Check for custom resolver
            if conflict.table_name in self.custom_resolvers:
                result = self.custom_resolvers[conflict.table_name](conflict)
                if result.success:
                    # Create a new record with the merged data
                    resolved = copy.deepcopy(conflict.server_record)
                    resolved.data = result.merged_data
                    resolved.version += 1
                    
                    # Mark as resolved
                    conflict.resolved_record = resolved
                    conflict.resolution_strategy = "custom"
                    
                    return resolved
                else:
                    # Failed to resolve with custom resolver
                    self._notify_conflict(conflict)
                    return None
            
            # Apply strategy
            if strategy == ConflictStrategy.SERVER_WINS.value:
                resolved = self._apply_server_wins(conflict)
                conflict.resolution_strategy = strategy
            elif strategy == ConflictStrategy.CLIENT_WINS.value:
                resolved = self._apply_client_wins(conflict)
                conflict.resolution_strategy = strategy
            elif strategy == ConflictStrategy.LAST_WRITE_WINS.value:
                resolved = self._apply_last_write_wins(conflict)
                conflict.resolution_strategy = strategy
            elif strategy == ConflictStrategy.CLIENT_PRIORITY.value:
                resolved = self._apply_client_priority(conflict)
                conflict.resolution_strategy = strategy
            elif strategy == ConflictStrategy.MERGE.value:
                result = self._apply_merge(conflict)
                if result.success:
                    # Create a new record with the merged data
                    resolved = copy.deepcopy(conflict.server_record)
                    resolved.data = result.merged_data
                    resolved.version += 1
                    conflict.resolution_strategy = strategy
                else:
                    # Could not merge automatically
                    self._notify_conflict(conflict)
                    return None
            elif strategy == ConflictStrategy.MANUAL.value:
                # Manual resolution requires user intervention
                self._notify_conflict(conflict)
                return None
            else:
                raise ValueError(f"Unknown conflict resolution strategy: {strategy}")
            
            # Mark as resolved
            conflict.resolved_record = resolved
            return resolved
        
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            self._notify_conflict(conflict)
            return None

    def manual_resolve(
        self,
        conflict: ConflictRecord,
        resolved_data: Dict[str, Any],
        resolved_by: str,
    ) -> Record:
        """Manually resolve a conflict with the provided data."""
        # Create a new record with the manually resolved data
        resolved = copy.deepcopy(conflict.server_record)
        resolved.data = resolved_data
        resolved.version += 1
        
        # Mark as resolved
        conflict.resolved_record = resolved
        conflict.resolution_strategy = "manual"
        conflict.resolved_by = resolved_by
        
        return resolved


class ConflictDetector:
    """Detects conflicts between client and server records."""

    def __init__(self, resolver: ConflictResolver):
        """Initialize a conflict detector with a resolver."""
        self.resolver = resolver
        self.conflicts: List[ConflictRecord] = []

    def detect_conflict(
        self,
        table_name: str,
        record_id: str,
        server_record: Record,
        client_record: Record,
    ) -> Optional[ConflictRecord]:
        """Detect if there is a conflict between server and client records."""
        # No conflict if records are identical
        if server_record.data == client_record.data:
            return None
        
        # Identify fields with conflicts
        field_conflicts = set()
        all_fields = set(server_record.data.keys()) | set(client_record.data.keys())
        
        for field in all_fields:
            server_value = server_record.data.get(field)
            client_value = client_record.data.get(field)
            
            if server_value != client_value:
                field_conflicts.add(field)
        
        if not field_conflicts:
            return None
        
        # Create a conflict record
        conflict = ConflictRecord(
            record_id=record_id,
            server_record=server_record,
            client_record=client_record,
            field_conflicts=field_conflicts,
            table_name=table_name,
        )
        
        # Store the conflict
        self.conflicts.append(conflict)
        
        return conflict

    def resolve_conflict(
        self,
        conflict: ConflictRecord,
        strategy: Optional[str] = None,
    ) -> Optional[Record]:
        """Resolve a conflict using the resolver."""
        return self.resolver.resolve(conflict, strategy)

    def get_conflicts(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        resolved: Optional[bool] = None,
    ) -> List[ConflictRecord]:
        """Get conflicts matching the given criteria."""
        result = []
        
        for conflict in self.conflicts:
            if table_name and conflict.table_name != table_name:
                continue
            
            if record_id and conflict.record_id != record_id:
                continue
            
            if resolved is not None:
                is_resolved = conflict.resolved_record is not None
                if resolved != is_resolved:
                    continue
            
            result.append(conflict)
        
        return result

    def get_unresolved_conflicts(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
    ) -> List[ConflictRecord]:
        """Get unresolved conflicts matching the given criteria."""
        return self.get_conflicts(table_name, record_id, resolved=False)

    def clear_resolved_conflicts(self) -> int:
        """Clear resolved conflicts from the history and return count."""
        resolved_count = sum(1 for c in self.conflicts if c.resolved_record is not None)
        self.conflicts = [c for c in self.conflicts if c.resolved_record is None]
        return resolved_count