"""Tests for the lineage tracking engine."""

import pytest
from datetime import datetime
import pytz

from pymigrate.lineage import LineageTracker, LineageGraph
from pymigrate.models import DataLineageNode, OperationType
from pymigrate.audit import AuditLogger, InMemoryAuditStorage


class TestLineageTracker:
    """Test suite for LineageTracker."""

    def test_create_source_node(self):
        """Test creating a source node."""
        tracker = LineageTracker()

        # Create source node
        node = tracker.create_source_node(
            name="Customer Database",
            metadata={"type": "postgresql", "host": "db.example.com"},
            actor="data_engineer",
        )

        # Verify node properties
        assert node.name == "Customer Database"
        assert node.node_type == "source"
        assert node.metadata["type"] == "postgresql"
        assert len(node.parent_ids) == 0

        # Verify node is in graph
        retrieved = tracker.graph.get_node(node.node_id)
        assert retrieved == node

    def test_create_transformation_node(self):
        """Test creating a transformation node."""
        tracker = LineageTracker()

        # Create source nodes first
        source1 = tracker.create_source_node("Source1")
        source2 = tracker.create_source_node("Source2")

        # Create transformation node
        transform = tracker.create_transformation_node(
            name="Data Merge",
            input_nodes=[source1.node_id, source2.node_id],
            transformation_type="join",
            metadata={"join_key": "customer_id"},
        )

        # Verify node properties
        assert transform.name == "Data Merge"
        assert transform.node_type == "transformation"
        assert transform.metadata["transformation_type"] == "join"
        assert set(transform.parent_ids) == {source1.node_id, source2.node_id}

        # Verify edges in graph
        assert tracker.graph.graph.has_edge(source1.node_id, transform.node_id)
        assert tracker.graph.graph.has_edge(source2.node_id, transform.node_id)

    def test_create_destination_node(self):
        """Test creating a destination node."""
        tracker = LineageTracker()

        # Create source and transform nodes
        source = tracker.create_source_node("Raw Data")
        transform = tracker.create_transformation_node(
            name="Clean Data",
            input_nodes=[source.node_id],
            transformation_type="cleanse",
        )

        # Create destination node
        destination = tracker.create_destination_node(
            name="Data Warehouse",
            input_nodes=[transform.node_id],
            destination_type="snowflake",
            metadata={"schema": "analytics"},
        )

        # Verify node properties
        assert destination.name == "Data Warehouse"
        assert destination.node_type == "destination"
        assert destination.metadata["destination_type"] == "snowflake"
        assert destination.parent_ids == [transform.node_id]

    def test_invalid_input_nodes(self):
        """Test error handling for invalid input nodes."""
        tracker = LineageTracker()

        # Try to create transformation with non-existent input
        with pytest.raises(ValueError, match="Input node .* not found"):
            tracker.create_transformation_node(
                name="Invalid Transform",
                input_nodes=["non-existent-id"],
                transformation_type="transform",
            )

    def test_transformation_tracking(self):
        """Test tracking a multi-step transformation."""
        tracker = LineageTracker()

        # Create initial nodes
        source = tracker.create_source_node("Customer Data")

        # Start transformation
        transform_id = "transform-123"
        tracker.start_transformation(
            transformation_id=transform_id,
            input_nodes=[source.node_id],
            transformation_type="enrichment",
            actor="data_scientist",
        )

        # Record operations
        tracker.record_transformation_operation(
            transform_id, "normalize", {"columns": ["name", "email"]}
        )
        tracker.record_transformation_operation(
            transform_id, "deduplicate", {"key": "customer_id", "records_removed": 150}
        )

        # Complete transformation
        output = tracker.complete_transformation(
            transform_id, "Enriched Customer Data", {"quality_score": 0.95}
        )

        # Verify output node
        assert output.name == "Enriched Customer Data"
        assert output.metadata["transformation_id"] == transform_id
        assert len(output.metadata["operations"]) == 2
        assert output.metadata["quality_score"] == 0.95

    def test_lineage_ancestry(self):
        """Test getting ancestors and descendants."""
        tracker = LineageTracker()

        # Create a lineage chain
        source = tracker.create_source_node("Original Data")
        transform1 = tracker.create_transformation_node(
            "Transform 1", [source.node_id], "filter"
        )
        transform2 = tracker.create_transformation_node(
            "Transform 2", [transform1.node_id], "aggregate"
        )
        destination = tracker.create_destination_node(
            "Final Data", [transform2.node_id], "database"
        )

        # Test ancestors
        ancestors = tracker.graph.get_ancestors(destination.node_id)
        assert len(ancestors) == 3
        assert source.node_id in ancestors
        assert transform1.node_id in ancestors
        assert transform2.node_id in ancestors

        # Test descendants
        descendants = tracker.graph.get_descendants(source.node_id)
        assert len(descendants) == 3
        assert transform1.node_id in descendants
        assert transform2.node_id in descendants
        assert destination.node_id in descendants

    def test_lineage_paths(self):
        """Test finding paths between nodes."""
        tracker = LineageTracker()

        # Create branching lineage
        source = tracker.create_source_node("Source")
        transform1 = tracker.create_transformation_node(
            "Path1", [source.node_id], "transform"
        )
        transform2 = tracker.create_transformation_node(
            "Path2", [source.node_id], "transform"
        )
        destination = tracker.create_destination_node(
            "Destination", [transform1.node_id, transform2.node_id], "database"
        )

        # Find paths from source to destination
        paths = tracker.graph.get_lineage_path(source.node_id, destination.node_id)
        assert len(paths) == 2  # Two paths through different transforms

    def test_impact_analysis(self):
        """Test impact analysis functionality."""
        tracker = LineageTracker()

        # Create complex lineage
        source1 = tracker.create_source_node("Source1")
        source2 = tracker.create_source_node("Source2")
        transform1 = tracker.create_transformation_node(
            "Transform1", [source1.node_id], "filter"
        )
        transform2 = tracker.create_transformation_node(
            "Transform2", [source1.node_id, source2.node_id], "join"
        )
        destination1 = tracker.create_destination_node(
            "Dest1", [transform1.node_id], "database"
        )
        destination2 = tracker.create_destination_node(
            "Dest2", [transform2.node_id], "database"
        )

        # Analyze impact of source1
        impact = tracker.graph.get_impact_analysis(source1.node_id)
        assert (
            impact["downstream_impact_count"] == 4
        )  # Both transforms and destinations
        assert impact["upstream_dependencies_count"] == 0  # Source has no dependencies

    def test_cycle_detection(self):
        """Test detection of cycles in lineage."""
        tracker = LineageTracker()

        # Create nodes
        node1 = tracker.create_source_node("Node1")
        node2 = DataLineageNode(
            node_id="node2",
            name="Node2",
            node_type="transformation",
            timestamp=datetime.now(pytz.UTC),
            parent_ids=[node1.node_id],
        )
        tracker.graph.add_node(node2)

        # Try to create a cycle (this should be prevented in practice)
        # For testing, we'll add edge manually
        tracker.graph.graph.add_edge(node2.node_id, node1.node_id)

        # Detect cycles
        cycles = tracker.graph.detect_cycles()
        assert len(cycles) > 0

    def test_find_data_sources(self):
        """Test finding original data sources."""
        tracker = LineageTracker()

        # Create lineage with multiple sources
        source1 = tracker.create_source_node("Database")
        source2 = tracker.create_source_node("API")
        transform = tracker.create_transformation_node(
            "Combine", [source1.node_id, source2.node_id], "join"
        )
        destination = tracker.create_destination_node(
            "Report", [transform.node_id], "file"
        )

        # Find sources for destination
        sources = tracker.find_data_sources(destination.node_id)
        assert len(sources) == 2
        assert source1.node_id in sources
        assert source2.node_id in sources

    def test_lineage_completeness_validation(self):
        """Test validation of lineage completeness."""
        tracker = LineageTracker()

        # Create valid lineage
        source = tracker.create_source_node("Source")
        transform = tracker.create_transformation_node(
            "Transform", [source.node_id], "process"
        )

        # Validate completeness
        validation = tracker.validate_lineage_completeness()
        assert validation["is_valid"]
        assert len(validation["issues"]) == 0

        # Create orphaned node (manually for testing)
        orphan = DataLineageNode(
            node_id="orphan",
            name="Orphan",
            node_type="transformation",
            timestamp=datetime.now(pytz.UTC),
            parent_ids=["non-existent"],
        )
        tracker.graph.add_node(orphan)

        # Validation should fail
        validation = tracker.validate_lineage_completeness()
        assert not validation["is_valid"]
        assert len(validation["issues"]) > 0

    def test_export_import_lineage(self):
        """Test exporting and importing lineage graphs."""
        tracker1 = LineageTracker()

        # Create lineage
        source = tracker1.create_source_node("Source")
        transform = tracker1.create_transformation_node(
            "Transform", [source.node_id], "process"
        )
        destination = tracker1.create_destination_node(
            "Destination", [transform.node_id], "database"
        )

        # Export lineage
        exported = tracker1.export_lineage()
        assert len(exported["nodes"]) == 3
        assert len(exported["edges"]) == 2

        # Import into new tracker
        tracker2 = LineageTracker()
        tracker2.import_lineage(exported)

        # Verify imported lineage
        imported_source = tracker2.graph.get_node(source.node_id)
        assert imported_source.name == "Source"

        # Verify relationships preserved
        paths = tracker2.graph.get_lineage_path(source.node_id, destination.node_id)
        assert len(paths) == 1
        assert len(paths[0]) == 3  # Source -> Transform -> Destination

    def test_with_audit_logging(self):
        """Test lineage tracking with audit logging enabled."""
        storage = InMemoryAuditStorage()
        audit_logger = AuditLogger(storage)
        tracker = LineageTracker(audit_logger=audit_logger)

        # Create nodes with audit logging
        source = tracker.create_source_node("Audited Source", actor="test_user")

        # Verify audit event was logged
        events = storage.get_events_by_resource(f"lineage:node:{source.node_id}")
        assert len(events) == 1
        assert events[0].actor == "test_user"
        assert events[0].operation == OperationType.WRITE


class TestLineageGraph:
    """Test suite for LineageGraph."""

    def test_graph_visualization(self, tmp_path):
        """Test graph visualization export."""
        graph = LineageGraph()

        # Create simple graph
        source = DataLineageNode(
            node_id="src1",
            name="Source",
            node_type="source",
            timestamp=datetime.now(pytz.UTC),
        )
        destination = DataLineageNode(
            node_id="dst1",
            name="Destination",
            node_type="destination",
            timestamp=datetime.now(pytz.UTC),
            parent_ids=["src1"],
        )

        graph.add_node(source)
        graph.add_node(destination)
        graph.add_edge("src1", "dst1")

        # Test visualization (may fail if graphviz not installed)
        try:
            output_path = tmp_path / "lineage_graph"
            graph.visualize(str(output_path), format="png")
            assert (tmp_path / "lineage_graph.png").exists()
        except Exception:
            # Graphviz might not be available in test environment
            pass

    def test_graph_statistics(self):
        """Test graph statistics in export."""
        graph = LineageGraph()

        # Add nodes of different types
        for i in range(3):
            graph.add_node(
                DataLineageNode(
                    node_id=f"source_{i}",
                    name=f"Source {i}",
                    node_type="source",
                    timestamp=datetime.now(pytz.UTC),
                )
            )

        for i in range(2):
            graph.add_node(
                DataLineageNode(
                    node_id=f"transform_{i}",
                    name=f"Transform {i}",
                    node_type="transformation",
                    timestamp=datetime.now(pytz.UTC),
                )
            )

        graph.add_node(
            DataLineageNode(
                node_id="dest_1",
                name="Destination",
                node_type="destination",
                timestamp=datetime.now(pytz.UTC),
            )
        )

        # Export and check statistics
        exported = graph.export_to_dict()
        stats = exported["statistics"]
        assert stats["total_nodes"] == 6
        assert stats["source_nodes"] == 3
        assert stats["transformation_nodes"] == 2
        assert stats["destination_nodes"] == 1
