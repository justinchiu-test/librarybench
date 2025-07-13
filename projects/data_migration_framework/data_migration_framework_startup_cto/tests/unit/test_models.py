"""Unit tests for PyMigrate models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from pymigrate.models.config import (
    ConflictResolutionStrategy,
    DatabaseType,
    DatabaseConfig,
    ServiceConfig,
    SyncConfig,
)
from pymigrate.models.data import (
    ChangeType,
    SyncDirection,
    SyncState,
    DataChange,
    ConflictReport,
    SyncStatus,
    ConsistencyReport,
)
from pymigrate.models.service import (
    HTTPMethod,
    ServiceType,
    RoutingStrategy,
    ServiceBoundary,
    APIEndpoint,
    RouteConfig,
    TrafficDistribution,
)


class TestConfigModels:
    """Test cases for configuration models."""
    
    def test_database_config_creation(self):
        """Test database configuration creation."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password",
        )
        
        assert config.type == DatabaseType.POSTGRESQL
        assert config.host == "localhost"
        assert config.port == 5432
        
    def test_database_config_invalid_port(self):
        """Test database config with invalid port."""
        with pytest.raises(ValidationError):
            DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=70000,  # Invalid port
                database="test_db",
                username="user",
                password="password",
            )
            
    def test_service_config_creation(self):
        """Test service configuration creation."""
        config = ServiceConfig(
            name="test_service",
            version="1.0.0",
            base_url="https://api.example.com",
            health_check_path="/health",
            timeout=30,
            retry_count=3,
        )
        
        assert config.name == "test_service"
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30
        
    def test_service_config_invalid_url(self):
        """Test service config with invalid URL."""
        with pytest.raises(ValidationError):
            ServiceConfig(
                name="test_service",
                version="1.0.0",
                base_url="not-a-url",  # Invalid URL
                health_check_path="/health",
            )
            
    def test_sync_config_creation(self):
        """Test sync configuration creation."""
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="source",
            port=5432,
            database="source_db",
            username="user",
            password="pass",
        )
        
        target_db = DatabaseConfig(
            type=DatabaseType.MYSQL,
            host="target",
            port=3306,
            database="target_db",
            username="user",
            password="pass",
        )
        
        config = SyncConfig(
            source_db=source_db,
            target_db=target_db,
            conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS,
            sync_interval_ms=100,
            batch_size=1000,
        )
        
        assert config.source_db == source_db
        assert config.target_db == target_db
        assert config.conflict_resolution == ConflictResolutionStrategy.LAST_WRITE_WINS
        
    def test_sync_config_custom_resolver_validation(self):
        """Test sync config custom resolver validation."""
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="db",
            username="user",
            password="pass",
        )
        
        # Should fail - custom resolver without CUSTOM strategy
        with pytest.raises(ValidationError):
            SyncConfig(
                source_db=source_db,
                target_db=source_db,
                conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS,
                custom_resolver="my.custom.resolver",
            )


class TestDataModels:
    """Test cases for data models."""
    
    def test_data_change_creation(self):
        """Test data change creation."""
        change = DataChange(
            id="change_123",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Test User"},
            metadata={"version": 1},
            source_system="source",
            checksum="abc123",
        )
        
        assert change.id == "change_123"
        assert change.table_name == "users"
        assert change.change_type == ChangeType.UPDATE
        
    def test_conflict_report_creation(self):
        """Test conflict report creation."""
        source_change = DataChange(
            id="src",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1},
            source_system="target",
        )
        
        report = ConflictReport(
            id="conflict_123",
            table_name="users",
            record_id="1",
            source_change=source_change,
            target_change=target_change,
            detected_at=datetime.utcnow(),
            resolution_strategy="last_write_wins",
            resolved=False,
        )
        
        assert report.id == "conflict_123"
        assert report.resolved is False
        
    def test_sync_status_creation(self):
        """Test sync status creation."""
        status = SyncStatus(
            sync_id="sync_123",
            direction=SyncDirection.BIDIRECTIONAL,
            state=SyncState.IN_PROGRESS,
            started_at=datetime.utcnow(),
            records_processed=100,
            records_synced=95,
            conflicts_detected=5,
        )
        
        assert status.sync_id == "sync_123"
        assert status.state == SyncState.IN_PROGRESS
        assert status.records_synced == 95
        
    def test_consistency_report_creation(self):
        """Test consistency report creation."""
        report = ConsistencyReport(
            validation_id="val_123",
            timestamp=datetime.utcnow(),
            tables_checked=["users", "orders"],
            total_records=1000,
            consistent_records=990,
            inconsistent_records=10,
            discrepancies=[],
            validation_duration_ms=5000,
            checksum_mismatches=[],
        )
        
        assert report.validation_id == "val_123"
        assert report.consistency_percentage == 99.0
        
    def test_consistency_report_percentage_calculation(self):
        """Test consistency percentage calculation."""
        report = ConsistencyReport(
            validation_id="val_123",
            timestamp=datetime.utcnow(),
            tables_checked=["users"],
            total_records=0,  # Edge case
            consistent_records=0,
            inconsistent_records=0,
            discrepancies=[],
            validation_duration_ms=100,
            checksum_mismatches=[],
        )
        
        assert report.consistency_percentage == 100.0  # No records = 100% consistent


class TestServiceModels:
    """Test cases for service models."""
    
    def test_service_boundary_creation(self):
        """Test service boundary creation."""
        boundary = ServiceBoundary(
            service_name="user_service",
            service_type=ServiceType.USER,
            tables=["users", "user_profiles"],
            relationships={"users": ["orders"]},
            access_patterns=[],
            estimated_size_mb=500.0,
            transaction_boundaries=["create_user"],
            dependencies={"orders"},
            confidence_score=0.85,
        )
        
        assert boundary.service_name == "user_service"
        assert boundary.service_type == ServiceType.USER
        assert len(boundary.tables) == 2
        
    def test_service_boundary_validation(self):
        """Test service boundary validation."""
        # Should fail - no tables
        with pytest.raises(ValidationError):
            ServiceBoundary(
                service_name="empty_service",
                service_type=ServiceType.CUSTOM,
                tables=[],  # Empty tables
                confidence_score=0.5,
            )
            
    def test_api_endpoint_creation(self):
        """Test API endpoint creation."""
        endpoint = APIEndpoint(
            path="/api/v1/users",
            method=HTTPMethod.GET,
            description="List users",
            query_parameters=[
                {"name": "page", "in": "query", "schema": {"type": "integer"}}
            ],
            authentication_required=True,
            rate_limit=100,
        )
        
        assert endpoint.path == "/api/v1/users"
        assert endpoint.method == HTTPMethod.GET
        assert endpoint.authentication_required is True
        
    def test_api_endpoint_path_validation(self):
        """Test API endpoint path validation."""
        # Should fail - path doesn't start with /
        with pytest.raises(ValidationError):
            APIEndpoint(
                path="api/v1/users",  # Missing leading /
                method=HTTPMethod.GET,
                description="Invalid path",
            )
            
    def test_route_config_creation(self):
        """Test route configuration creation."""
        config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=25.0,
            sticky_sessions=True,
            health_check_interval_ms=5000,
            rollback_enabled=True,
        )
        
        assert config.service_name == "user_service"
        assert config.percentage == 25.0
        assert config.sticky_sessions is True
        
    def test_route_config_percentage_validation(self):
        """Test route config percentage validation."""
        # Should succeed - percentage within range
        config = RouteConfig(
            service_name="test",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=50.0,
        )
        assert config.percentage == 50.0
        
        # Should fail - percentage out of range
        with pytest.raises(ValidationError):
            RouteConfig(
                service_name="test",
                strategy=RoutingStrategy.PERCENTAGE,
                percentage=150.0,  # Over 100%
            )
            
    def test_traffic_distribution_creation(self):
        """Test traffic distribution creation."""
        distribution = TrafficDistribution(
            timestamp=datetime.utcnow(),
            distributions={"service_a": 50.0, "service_b": 50.0},
            total_requests=10000,
            success_rate=99.5,
            average_latency_ms=25.5,
            error_counts={"service_a": 10, "service_b": 5},
            active_routes=[],
        )
        
        assert distribution.total_requests == 10000
        assert distribution.success_rate == 99.5
        
    def test_traffic_distribution_validation(self):
        """Test traffic distribution validation."""
        # Should fail - distributions don't sum to 100%
        with pytest.raises(ValidationError):
            TrafficDistribution(
                timestamp=datetime.utcnow(),
                distributions={"service_a": 30.0, "service_b": 40.0},  # Sums to 70%
                total_requests=1000,
                success_rate=100.0,
                average_latency_ms=10.0,
                error_counts={},
                active_routes=[],
            )
            
    def test_all_enums(self):
        """Test all enum values are accessible."""
        # Test ChangeType
        assert ChangeType.INSERT.value == "insert"
        assert ChangeType.UPDATE.value == "update"
        assert ChangeType.DELETE.value == "delete"
        
        # Test SyncDirection
        assert SyncDirection.SOURCE_TO_TARGET.value == "source_to_target"
        assert SyncDirection.TARGET_TO_SOURCE.value == "target_to_source"
        assert SyncDirection.BIDIRECTIONAL.value == "bidirectional"
        
        # Test SyncState
        assert SyncState.PENDING.value == "pending"
        assert SyncState.IN_PROGRESS.value == "in_progress"
        assert SyncState.COMPLETED.value == "completed"
        assert SyncState.FAILED.value == "failed"
        assert SyncState.CONFLICT.value == "conflict"
        
        # Test HTTPMethod
        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"
        assert HTTPMethod.PUT.value == "PUT"
        assert HTTPMethod.DELETE.value == "DELETE"
        assert HTTPMethod.PATCH.value == "PATCH"
        
        # Test ServiceType
        assert ServiceType.USER.value == "user"
        assert ServiceType.ORDER.value == "order"
        assert ServiceType.INVENTORY.value == "inventory"
        assert ServiceType.PAYMENT.value == "payment"
        assert ServiceType.NOTIFICATION.value == "notification"
        assert ServiceType.ANALYTICS.value == "analytics"
        assert ServiceType.CUSTOM.value == "custom"
        
        # Test RoutingStrategy
        assert RoutingStrategy.PERCENTAGE.value == "percentage"
        assert RoutingStrategy.CANARY.value == "canary"
        assert RoutingStrategy.BLUE_GREEN.value == "blue_green"
        assert RoutingStrategy.FEATURE_FLAG.value == "feature_flag"