"""Unit tests for Conflict Resolver."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from pymigrate.sync.conflict_resolver import ConflictResolver
from pymigrate.models.config import ConflictResolutionStrategy
from pymigrate.models.data import DataChange, ChangeType, ConflictReport


class TestConflictResolver:
    """Test cases for Conflict Resolver."""
    
    def test_conflict_resolver_initialization(self):
        """Test conflict resolver initialization."""
        resolver = ConflictResolver(ConflictResolutionStrategy.LAST_WRITE_WINS)
        
        assert resolver.strategy == ConflictResolutionStrategy.LAST_WRITE_WINS
        
    @pytest.mark.asyncio
    async def test_resolve_last_write_wins(self):
        """Test last write wins resolution strategy."""
        resolver = ConflictResolver(ConflictResolutionStrategy.LAST_WRITE_WINS)
        
        # Source change is older
        source_change = DataChange(
            id="src_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() - timedelta(hours=1),
            data={"id": 1, "name": "Old Name"},
            source_system="source",
        )
        
        # Target change is newer
        target_change = DataChange(
            id="tgt_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "New Name"},
            source_system="target",
        )
        
        resolved = await resolver.resolve_conflict(source_change, target_change)
        
        # Should choose target (newer)
        assert resolved == target_change
        
    @pytest.mark.asyncio
    async def test_resolve_source_wins(self):
        """Test source wins resolution strategy."""
        resolver = ConflictResolver(ConflictResolutionStrategy.SOURCE_WINS)
        
        source_change = DataChange(
            id="src_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Source Name"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() + timedelta(hours=1),
            data={"id": 1, "name": "Target Name"},
            source_system="target",
        )
        
        resolved = await resolver.resolve_conflict(source_change, target_change)
        
        # Should always choose source
        assert resolved == source_change
        
    @pytest.mark.asyncio
    async def test_resolve_target_wins(self):
        """Test target wins resolution strategy."""
        resolver = ConflictResolver(ConflictResolutionStrategy.TARGET_WINS)
        
        source_change = DataChange(
            id="src_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() + timedelta(hours=1),
            data={"id": 1, "name": "Source Name"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Target Name"},
            source_system="target",
        )
        
        resolved = await resolver.resolve_conflict(source_change, target_change)
        
        # Should always choose target
        assert resolved == target_change
        
    @pytest.mark.asyncio
    async def test_resolve_merge_strategy(self):
        """Test merge resolution strategy."""
        resolver = ConflictResolver(ConflictResolutionStrategy.MERGE)
        
        source_change = DataChange(
            id="src_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Source Name", "email": "source@example.com"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Target Name", "phone": "+1234567890"},
            source_system="target",
        )
        
        resolved = await resolver.resolve_conflict(source_change, target_change)
        
        # Should merge data
        assert resolved.data["id"] == 1
        assert resolved.data["name"] in ["Source Name", "Target Name"]  # One wins
        assert resolved.data["email"] == "source@example.com"  # From source
        assert resolved.data["phone"] == "+1234567890"  # From target
        
    @pytest.mark.asyncio
    async def test_resolve_custom_strategy(self):
        """Test custom resolution strategy."""
        async def custom_resolver(source, target):
            # Custom logic: prefer longer string values
            merged_data = {}
            all_keys = set(source.data.keys()) | set(target.data.keys())
            
            for key in all_keys:
                source_val = source.data.get(key, "")
                target_val = target.data.get(key, "")
                
                if isinstance(source_val, str) and isinstance(target_val, str):
                    merged_data[key] = source_val if len(source_val) > len(target_val) else target_val
                else:
                    merged_data[key] = target_val  # Default to target
                    
            return DataChange(
                id=f"merged_{source.id}_{target.id}",
                table_name=source.table_name,
                change_type=source.change_type,
                timestamp=max(source.timestamp, target.timestamp),
                data=merged_data,
                source_system="merged",
            )
        
        resolver = ConflictResolver(
            ConflictResolutionStrategy.CUSTOM,
            custom_resolver=custom_resolver
        )
        
        source_change = DataChange(
            id="src_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "A", "description": "Very long description"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt_1",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Longer Name", "description": "Short"},
            source_system="target",
        )
        
        resolved = await resolver.resolve_conflict(source_change, target_change)
        
        assert resolved.data["name"] == "Longer Name"  # Longer from target
        assert resolved.data["description"] == "Very long description"  # Longer from source