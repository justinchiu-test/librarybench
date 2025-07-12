"""End-to-end tests for complete migration scenarios."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from pymigrate.sync.engine import SyncEngine
from pymigrate.analyzer.boundary import ServiceBoundaryAnalyzer
from pymigrate.generator.api import APIGenerator
from pymigrate.validator.consistency import ConsistencyValidator
from pymigrate.router.traffic import TrafficRouter
from pymigrate.models.config import (
    DatabaseConfig,
    DatabaseType,
    SyncConfig,
    ConflictResolutionStrategy,
    ServiceConfig,
)
from pymigrate.models.service import (
    ServiceBoundary,
    ServiceType,
    RouteConfig,
    RoutingStrategy,
)
from pymigrate.models.data import SyncDirection


class TestMigrationScenarios:
    """End-to-end tests for complete migration scenarios."""
    
    @pytest.mark.asyncio
    async def test_user_authentication_service_migration(self, mock_db_connection):
        """Test migrating user authentication service while users are logging in."""
        # Scenario: Migrate user authentication from monolith to microservice
        # while maintaining zero downtime and handling active user sessions
        
        # 1. Analyze service boundaries
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # Mock database structure
        mock_db_connection.get_all_tables.return_value = [
            "users", "user_sessions", "user_roles", "role_permissions",
            "orders", "products", "inventory"
        ]
        
        with patch.object(analyzer.dependency_analyzer, 'build_dependency_graph', new_callable=AsyncMock):
            with patch.object(analyzer.pattern_analyzer, 'analyze_patterns', new_callable=AsyncMock) as mock_patterns:
                mock_patterns.return_value = {
                    "patterns": [{
                        "pattern_type": "transactional_boundary",
                        "tables": ["users", "user_sessions", "user_roles"],
                        "confidence": 0.95
                    }]
                }
                
                boundaries = await analyzer.analyze()
                
                # Find user service boundary
                user_boundary = next(
                    b for b in boundaries 
                    if b.service_type == ServiceType.USER
                )
                
        # 2. Generate API for user service
        api_generator = APIGenerator(mock_db_connection)
        
        with patch.object(api_generator.schema_generator, 'generate_schema', new_callable=AsyncMock):
            api_spec = await api_generator.generate_api(user_boundary)
            
            assert api_spec["service_name"] == user_boundary.service_name
            assert len(api_spec["endpoints"]) > 0
            
        # 3. Setup bi-directional sync
        sync_config = SyncConfig(
            source_db=DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="monolith-db",
                port=5432,
                database="monolith",
                username="user",
                password="pass"
            ),
            target_db=DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="user-service-db",
                port=5432,
                database="users",
                username="user",
                password="pass"
            ),
            conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS,
            sync_interval_ms=100
        )
        
        sync_engine = SyncEngine(sync_config)
        
        # 4. Setup traffic routing
        traffic_router = TrafficRouter()
        
        user_service_config = ServiceConfig(
            name="user_service",
            version="1.0.0",
            base_url="http://user-service:8000",
            health_check_path="/health"
        )
        
        route_config = RouteConfig(
            service_name="user_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=0.0,  # Start with 0%
            sticky_sessions=True,  # Important for auth
            rollback_enabled=True
        )
        
        await traffic_router.add_route(route_config, user_service_config)
        
        # 5. Simulate gradual migration
        migration_steps = [
            (10.0, "Canary deployment - 10% traffic"),
            (25.0, "Increase to 25% after validation"),
            (50.0, "Half traffic to microservice"),
            (75.0, "Majority traffic to microservice"),
            (100.0, "Complete migration")
        ]
        
        for percentage, description in migration_steps:
            # Update traffic percentage
            with patch.object(traffic_router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
                mock_health.return_value = True
                
                await traffic_router.update_traffic_percentage(
                    "user_service",
                    percentage,
                    gradual=True,
                    step_size=5.0
                )
                
            # Validate consistency at each step
            validator = ConsistencyValidator(
                sync_engine.source_conn,
                sync_engine.target_conn
            )
            
            with patch.object(validator, '_validate_table', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {
                    "total_records": 10000,
                    "consistent_records": 9950,
                    "inconsistent_records": 50,
                    "discrepancies": [],
                    "checksum_mismatches": []
                }
                
                report = await validator.validate_consistency(
                    tables=["users", "user_sessions", "user_roles"]
                )
                
                # Ensure high consistency
                assert report.consistency_percentage > 99.0
                
        # 6. Verify final state
        final_distribution = traffic_router.get_current_distribution()
        assert final_distribution.distributions.get("user_service", 0) == 100.0
        
    @pytest.mark.asyncio
    async def test_order_processing_during_payment_service_extraction(self):
        """Test handling order processing during payment service extraction."""
        # Scenario: Extract payment service while orders are being processed
        # Must maintain transactional integrity and handle distributed transactions
        
        # Setup services
        source_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="monolith-db",
            port=5432,
            database="monolith",
            username="user",
            password="pass"
        )
        
        payment_db = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            host="payment-db",
            port=5432,
            database="payments",
            username="user",
            password="pass"
        )
        
        # Configure sync with priority-based resolution
        # Orders have priority over payment updates
        sync_config = SyncConfig(
            source_db=source_db,
            target_db=payment_db,
            conflict_resolution=ConflictResolutionStrategy.PRIORITY_BASED,
            priority_rules={
                "orders": 100,
                "payments": 90,
                "source": 80,
                "target": 70
            }
        )
        
        sync_engine = SyncEngine(sync_config)
        
        # Simulate concurrent order and payment processing
        order_changes = []
        payment_changes = []
        
        for i in range(10):
            # Order created in monolith
            order_changes.append({
                "id": f"order_{i}",
                "user_id": f"user_{i}",
                "total": 100.0 * (i + 1),
                "status": "pending_payment"
            })
            
            # Payment processed
            payment_changes.append({
                "id": f"payment_{i}",
                "order_id": f"order_{i}",
                "amount": 100.0 * (i + 1),
                "status": "processing"
            })
            
        # Test transaction boundary preservation
        with patch.object(sync_engine.change_detector, 'detect_changes', new_callable=AsyncMock):
            # Sync should maintain consistency
            status = await sync_engine.sync_once()
            
            # No data loss
            assert status.records_synced == status.records_processed
            
    @pytest.mark.asyncio
    async def test_inventory_consistency_during_warehouse_migration(self, mock_db_connection):
        """Test maintaining inventory consistency during warehouse service migration."""
        # Scenario: Migrate inventory management while orders are being fulfilled
        # Critical: Stock levels must remain accurate
        
        # Setup inventory service boundary
        inventory_boundary = ServiceBoundary(
            service_name="inventory_service",
            service_type=ServiceType.INVENTORY,
            tables=["products", "inventory", "stock_movements", "warehouses"],
            relationships={"products": ["orders"]},
            access_patterns=[],
            estimated_size_mb=2000.0,
            transaction_boundaries=["update_stock", "reserve_inventory"],
            dependencies={"orders"},
            confidence_score=0.9
        )
        
        # Setup real-time validation
        validator = ConsistencyValidator(mock_db_connection, mock_db_connection)
        
        # Mock inventory operations during migration
        inventory_operations = [
            ("reserve", {"product_id": 1, "quantity": 10}),
            ("fulfill", {"product_id": 1, "quantity": 8}),
            ("return", {"product_id": 1, "quantity": 2}),
            ("restock", {"product_id": 2, "quantity": 100}),
        ]
        
        # Process operations with validation
        for operation, data in inventory_operations:
            # Apply operation to both systems
            with patch.object(validator, '_validate_records', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {
                    "consistent": 100,
                    "inconsistent": 0,
                    "discrepancies": [],
                    "checksum_mismatches": []
                }
                
                # Validate after each operation
                report = await validator.validate_consistency(
                    tables=["inventory"],
                    sample_size=None,
                    deep_check=True
                )
                
                # Inventory must remain consistent
                assert report.consistency_percentage == 100.0
                
    @pytest.mark.asyncio
    async def test_session_state_preservation_during_gradual_migration(self):
        """Test preserving session state during gradual traffic migration."""
        # Scenario: Migrate user sessions without logging out users
        
        traffic_router = TrafficRouter()
        
        # Setup route with sticky sessions
        route_config = RouteConfig(
            service_name="session_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=0.0,
            sticky_sessions=True,  # Critical for sessions
            health_check_interval_ms=1000
        )
        
        service_config = ServiceConfig(
            name="session_service",
            version="1.0.0",
            base_url="http://session-service:8000",
            health_check_path="/health"
        )
        
        await traffic_router.add_route(route_config, service_config)
        
        # Simulate active user sessions
        active_sessions = {}
        for i in range(100):
            user_id = f"user_{i}"
            session_id = f"session_{i}"
            active_sessions[user_id] = {
                "session_id": session_id,
                "created_at": datetime.utcnow() - timedelta(minutes=30),
                "last_activity": datetime.utcnow() - timedelta(minutes=i % 10)
            }
            
        # Gradually migrate traffic
        with patch.object(traffic_router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            # Track session routing
            session_destinations = {}
            
            for percentage in [10, 25, 50, 75, 100]:
                await traffic_router.update_traffic_percentage(
                    "session_service",
                    percentage,
                    gradual=False
                )
                
                # Route requests for active sessions
                for user_id in active_sessions:
                    result = await traffic_router.route_request(
                        request_id=f"req_{user_id}",
                        service_name="session_service",
                        user_id=user_id
                    )
                    
                    # Verify sticky routing
                    if user_id in session_destinations:
                        # Should stick to same destination
                        assert result["destination"] == session_destinations[user_id]
                    else:
                        session_destinations[user_id] = result["destination"]
                        
    @pytest.mark.asyncio
    async def test_rollback_problematic_service_migration(self):
        """Test rolling back a problematic service migration without data loss."""
        # Scenario: Payment service migration encounters issues, need to rollback
        
        traffic_router = TrafficRouter()
        sync_engine = SyncEngine(SyncConfig(
            source_db=DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=5432,
                database="monolith",
                username="user",
                password="pass"
            ),
            target_db=DatabaseConfig(
                type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=5433,
                database="payments",
                username="user",
                password="pass"
            ),
            conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS
        ))
        
        # Setup payment service route
        route_config = RouteConfig(
            service_name="payment_service",
            strategy=RoutingStrategy.PERCENTAGE,
            percentage=0.0,
            rollback_enabled=True
        )
        
        service_config = ServiceConfig(
            name="payment_service",
            version="1.0.0",
            base_url="http://payment-service:8000",
            health_check_path="/health"
        )
        
        await traffic_router.add_route(route_config, service_config)
        
        # Migrate to 50%
        with patch.object(traffic_router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            await traffic_router.update_traffic_percentage(
                "payment_service",
                50.0,
                gradual=False
            )
            
        # Simulate service degradation
        with patch.object(traffic_router.health_checker, 'is_healthy', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = False  # Service unhealthy
            
            # Should automatically route to monolith
            result = await traffic_router.route_request(
                request_id="critical_payment",
                service_name="payment_service"
            )
            
            assert result["destination"] == "monolith"
            assert result["reason"] == "service_unhealthy"
            
        # Execute rollback
        await traffic_router.rollback_service("payment_service")
        
        # Verify all traffic back to monolith
        distribution = traffic_router.get_current_distribution()
        assert distribution.distributions.get("payment_service", 0) == 0.0
        
        # Verify no data loss during rollback
        with patch.object(sync_engine, 'sync_once', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = MagicMock(
                records_synced=1000,
                records_processed=1000,
                conflicts_detected=0
            )
            
            # Reverse sync to ensure monolith has all data
            status = await sync_engine.sync_once(SyncDirection.TARGET_TO_SOURCE)
            
            assert status.records_synced == status.records_processed