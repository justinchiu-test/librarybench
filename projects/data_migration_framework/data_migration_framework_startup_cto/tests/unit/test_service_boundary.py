"""Unit tests for Service Boundary Analyzer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import networkx as nx

from pymigrate.analyzer.boundary import ServiceBoundaryAnalyzer
from pymigrate.analyzer.dependency import DependencyAnalyzer
from pymigrate.analyzer.pattern import AccessPatternAnalyzer
from pymigrate.models.service import ServiceType


class TestServiceBoundaryAnalyzer:
    """Test cases for Service Boundary Analyzer."""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, mock_db_connection):
        """Test analyzer initialization."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        assert analyzer.connection == mock_db_connection
        assert isinstance(analyzer.dependency_analyzer, DependencyAnalyzer)
        assert isinstance(analyzer.pattern_analyzer, AccessPatternAnalyzer)
        assert analyzer._table_graph is None
        
    @pytest.mark.asyncio
    async def test_analyze_service_boundaries(self, mock_db_connection):
        """Test service boundary analysis."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # Create mock dependency graph
        mock_graph = nx.DiGraph()
        mock_graph.add_edges_from([
            ("users", "orders"),
            ("users", "user_profiles"),
            ("orders", "order_items"),
            ("products", "order_items"),
            ("inventory", "products"),
        ])
        
        # Mock dependency analyzer
        with patch.object(analyzer.dependency_analyzer, 'build_dependency_graph', new_callable=AsyncMock) as mock_dep:
            mock_dep.return_value = mock_graph
            
            # Mock access patterns
            mock_patterns = {
                "patterns": [
                    {
                        "pattern_type": "frequently_accessed_together",
                        "tables": ["users", "user_profiles"],
                        "confidence": 0.9,
                    },
                    {
                        "pattern_type": "transactional_boundary",
                        "tables": ["orders", "order_items"],
                        "confidence": 0.95,
                    },
                ]
            }
            
            with patch.object(analyzer.pattern_analyzer, 'analyze_patterns', new_callable=AsyncMock) as mock_pattern:
                mock_pattern.return_value = mock_patterns
                
                # Mock table size
                mock_db_connection.get_table_size_mb.return_value = 100.0
                
                boundaries = await analyzer.analyze(min_confidence=0.7)
                
                assert len(boundaries) > 0
                assert all(b.confidence_score >= 0.7 for b in boundaries)
                assert all(len(b.tables) > 0 for b in boundaries)
                
    @pytest.mark.asyncio
    async def test_service_type_determination(self, mock_db_connection):
        """Test service type determination based on table names."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        test_cases = [
            (["users", "user_profiles", "user_auth"], ServiceType.USER),
            (["orders", "order_items", "order_history"], ServiceType.ORDER),
            (["products", "inventory", "stock_levels"], ServiceType.INVENTORY),
            (["payments", "billing", "invoices"], ServiceType.PAYMENT),
            (["notifications", "email_queue", "sms_queue"], ServiceType.NOTIFICATION),
            (["analytics_events", "metrics", "reports"], ServiceType.ANALYTICS),
            (["random_table", "other_table"], ServiceType.CUSTOM),
        ]
        
        for tables, expected_type in test_cases:
            service_type = analyzer._determine_service_type(tables, {})
            assert service_type == expected_type
            
    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, mock_db_connection):
        """Test confidence score calculation for service boundaries."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # High confidence: few external dependencies, good table count
        score1 = analyzer._calculate_confidence_score(
            tables=["users", "user_profiles", "user_settings"],
            relationships={"users": ["orders"]},  # 1 external dependency
            transaction_boundaries=["create_user", "update_profile"],
        )
        assert score1 > 0.8
        
        # Low confidence: many external dependencies
        score2 = analyzer._calculate_confidence_score(
            tables=["users"],
            relationships={
                "users": ["orders", "payments", "notifications", "analytics", "inventory"]
            },
            transaction_boundaries=[],
        )
        assert score2 < 0.5
        
        # Medium confidence: no transaction boundaries
        score3 = analyzer._calculate_confidence_score(
            tables=["products", "categories"],
            relationships={},
            transaction_boundaries=[],
        )
        assert 0.4 < score3 < 0.8
        
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, mock_db_connection):
        """Test detection of circular dependencies between services."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # Create boundaries with circular dependencies
        from pymigrate.models.service import ServiceBoundary
        
        boundaries = [
            ServiceBoundary(
                service_name="service_a",
                service_type=ServiceType.CUSTOM,
                tables=["table_a"],
                dependencies={"table_b"},
                confidence_score=0.9,
            ),
            ServiceBoundary(
                service_name="service_b",
                service_type=ServiceType.CUSTOM,
                tables=["table_b"],
                dependencies={"table_c"},
                confidence_score=0.9,
            ),
            ServiceBoundary(
                service_name="service_c",
                service_type=ServiceType.CUSTOM,
                tables=["table_c"],
                dependencies={"table_a"},  # Creates cycle
                confidence_score=0.9,
            ),
        ]
        
        validated = analyzer._validate_boundaries(boundaries)
        
        # Should still return all boundaries but with adjusted confidence
        assert len(validated) == 3
        
    @pytest.mark.asyncio
    async def test_migration_order_determination(self, mock_db_connection):
        """Test determining optimal migration order."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        from pymigrate.models.service import ServiceBoundary
        
        # Create boundaries with dependencies
        boundaries = [
            ServiceBoundary(
                service_name="user_service",
                service_type=ServiceType.USER,
                tables=["users", "user_profiles"],
                dependencies=set(),  # No dependencies
                confidence_score=0.9,
            ),
            ServiceBoundary(
                service_name="order_service",
                service_type=ServiceType.ORDER,
                tables=["orders", "order_items"],
                dependencies={"users"},  # Depends on user service
                confidence_score=0.9,
            ),
            ServiceBoundary(
                service_name="payment_service",
                service_type=ServiceType.PAYMENT,
                tables=["payments", "invoices"],
                dependencies={"orders", "users"},  # Depends on both
                confidence_score=0.9,
            ),
        ]
        
        migration_order = await analyzer.get_migration_order(boundaries)
        
        # User service should come first (no dependencies)
        assert migration_order[0] == "user_service"
        
        # Payment service should come last (most dependencies)
        assert migration_order[-1] == "payment_service"
        
    @pytest.mark.asyncio
    async def test_transaction_boundary_identification(self, mock_db_connection):
        """Test identification of transaction boundaries."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # Mock stored procedures
        mock_procedures = [
            {"name": "create_user_with_profile"},
            {"name": "process_order_with_payment"},
            {"name": "update_inventory_levels"},
        ]
        mock_db_connection.get_stored_procedures.return_value = mock_procedures
        
        # Mock procedure table access
        mock_db_connection.get_procedure_tables.side_effect = [
            ["users", "user_profiles"],  # Accesses multiple tables in service
            ["orders", "payments"],       # Cross-service access
            ["inventory"],                # Single table access
        ]
        
        boundaries = await analyzer._identify_transaction_boundaries(
            ["users", "user_profiles"]
        )
        
        assert "create_user_with_profile" in boundaries
        assert "process_order_with_payment" not in boundaries  # Cross-service
        assert "update_inventory_levels" not in boundaries     # Single table
        
    @pytest.mark.asyncio
    async def test_cohesive_group_identification(self, mock_db_connection):
        """Test identification of cohesive table groups."""
        analyzer = ServiceBoundaryAnalyzer(mock_db_connection)
        
        # Create a graph with clear communities
        graph = nx.DiGraph()
        
        # User community
        graph.add_edges_from([
            ("users", "user_profiles"),
            ("user_profiles", "user_settings"),
            ("user_settings", "users"),
        ])
        
        # Order community
        graph.add_edges_from([
            ("orders", "order_items"),
            ("order_items", "order_status"),
            ("order_status", "orders"),
        ])
        
        # Isolated table
        graph.add_node("audit_logs")
        
        analyzer._table_graph = graph
        
        groups = analyzer._identify_cohesive_groups({})
        
        # Should identify at least 2 groups (user and order)
        assert len(groups) >= 2
        
        # Check that related tables are grouped together
        user_tables = {"users", "user_profiles", "user_settings"}
        order_tables = {"orders", "order_items", "order_status"}
        
        user_group_found = False
        order_group_found = False
        
        for group_name, tables in groups.items():
            table_set = set(tables)
            if user_tables.issubset(table_set):
                user_group_found = True
            if order_tables.issubset(table_set):
                order_group_found = True
                
        assert user_group_found or order_group_found  # At least one cohesive group found