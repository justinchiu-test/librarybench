"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from pymigrate.models.config import (
    DatabaseConfig,
    DatabaseType,
    SyncConfig,
    ConflictResolutionStrategy,
    ServiceConfig,
)
from pymigrate.models.data import DataChange, ChangeType
from pymigrate.models.service import ServiceBoundary, ServiceType
from pymigrate.utils.database import DatabaseConnection


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def source_db_config():
    """Source database configuration."""
    return DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="source_db",
        username="user",
        password="password",
    )


@pytest.fixture
def target_db_config():
    """Target database configuration."""
    return DatabaseConfig(
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5433,
        database="target_db",
        username="user",
        password="password",
    )


@pytest.fixture
def sync_config(source_db_config, target_db_config):
    """Sync configuration."""
    return SyncConfig(
        source_db=source_db_config,
        target_db=target_db_config,
        conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS,
        sync_interval_ms=100,
        batch_size=1000,
    )


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    conn = AsyncMock()
    
    # Setup default return values
    conn.get_all_tables.return_value = ["users", "orders", "products"]
    conn.get_table_count.return_value = 1000
    conn.get_primary_key.return_value = "id"
    conn.get_table_columns.return_value = [
        {"name": "id", "type": "integer", "nullable": False},
        {"name": "name", "type": "varchar", "nullable": False},
        {"name": "email", "type": "varchar", "nullable": True},
        {"name": "created_at", "type": "timestamp", "nullable": False},
    ]
    conn.get_foreign_keys.return_value = []
    conn.supports_cdc = True
    conn.supports_soft_delete = True
    conn.database_name = "test_db"
    conn.get_records_by_ids.return_value = []
    conn.get_sample_records.return_value = []
    conn.get_table_size_mb.return_value = 100.0
    conn.get_stored_procedures.return_value = []
    conn.get_procedure_tables.return_value = []
    conn.get_table_constraints.return_value = []
    conn.get_tracked_tables.return_value = ["users", "orders", "products"]
    conn.get_last_processed_log_id.return_value = 0
    conn.query_change_log.return_value = []
    conn.query_modified_records.return_value = []
    conn.query_deleted_records.return_value = []
    conn.get_all_primary_keys.return_value = []
    conn.get_table_metadata.return_value = {}
    conn.get_sample_data.return_value = []
    conn.close.return_value = None
    conn.execute.return_value = None
    conn.fetch.return_value = []
    conn.transaction.return_value = AsyncMock()
    conn.batch_insert.return_value = None
    conn.is_healthy.return_value = True
    conn.enable_cdc.return_value = None
    conn.ensure_timestamp_columns.return_value = None
    
    return conn


@pytest.fixture
def sample_data_change():
    """Sample data change object."""
    return DataChange(
        id="change_123",
        table_name="users",
        change_type=ChangeType.UPDATE,
        timestamp=datetime.utcnow(),
        data={
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "updated_at": datetime.utcnow().isoformat(),
        },
        metadata={"version": 1},
        source_system="source",
        checksum="abc123",
    )


@pytest.fixture
def service_config():
    """Service configuration."""
    return ServiceConfig(
        name="user_service",
        version="1.0.0",
        base_url="http://localhost:8000",
        health_check_path="/health",
        timeout=30,
        retry_count=3,
    )


@pytest.fixture
def sample_service_boundary():
    """Sample service boundary."""
    return ServiceBoundary(
        service_name="user_service",
        service_type=ServiceType.USER,
        tables=["users", "user_profiles", "user_preferences"],
        relationships={"users": ["orders", "sessions"]},
        access_patterns=[
            {
                "pattern_type": "frequently_accessed_together",
                "tables": ["users", "user_profiles"],
                "confidence": 0.9,
            }
        ],
        estimated_size_mb=500.0,
        transaction_boundaries=["create_user", "update_profile"],
        dependencies={"orders", "sessions"},
        confidence_score=0.85,
    )


@pytest.fixture
def mock_health_response():
    """Mock health check response."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "database": "healthy",
            "cache": "healthy",
        },
    }


@pytest.fixture
def sample_table_data():
    """Sample table data for testing."""
    return [
        {
            "id": 1,
            "name": "User 1",
            "email": "user1@example.com",
            "created_at": datetime.utcnow(),
        },
        {
            "id": 2,
            "name": "User 2",
            "email": "user2@example.com",
            "created_at": datetime.utcnow(),
        },
        {
            "id": 3,
            "name": "User 3",
            "email": "user3@example.com",
            "created_at": datetime.utcnow(),
        },
    ]