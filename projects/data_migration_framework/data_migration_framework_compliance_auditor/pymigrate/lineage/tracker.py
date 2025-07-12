"""Lineage tracking engine implementation."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz

from pymigrate.audit.logger import AuditLogger
from pymigrate.lineage.graph import LineageGraph
from pymigrate.models import DataLineageNode, OperationType


class LineageTracker:
    """Tracks data lineage through migrations and transformations."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize the lineage tracker.

        Args:
            audit_logger: Optional audit logger for tracking lineage operations
        """
        self.graph = LineageGraph()
        self.audit_logger = audit_logger
        self._active_transformations: Dict[str, Dict[str, Any]] = {}

    def create_source_node(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        actor: Optional[str] = None,
    ) -> DataLineageNode:
        """Create a source node in the lineage graph.

        Args:
            name: Name of the data source
            metadata: Additional metadata about the source
            actor: User creating the source node

        Returns:
            Created source node
        """
        node = DataLineageNode(
            node_id=str(uuid.uuid4()),
            name=name,
            node_type="source",
            timestamp=datetime.now(pytz.UTC),
            metadata=metadata or {},
        )

        self.graph.add_node(node)

        # Log the operation
        if self.audit_logger and actor:
            self.audit_logger.log_event(
                actor=actor,
                operation=OperationType.WRITE,
                resource=f"lineage:node:{node.node_id}",
                details={
                    "action": "create_source_node",
                    "node_name": name,
                    "node_type": "source",
                },
            )

        return node

    def create_transformation_node(
        self,
        name: str,
        input_nodes: List[str],
        transformation_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        actor: Optional[str] = None,
    ) -> DataLineageNode:
        """Create a transformation node in the lineage graph.

        Args:
            name: Name of the transformation
            input_nodes: List of input node IDs
            transformation_type: Type of transformation applied
            metadata: Additional metadata about the transformation
            actor: User creating the transformation

        Returns:
            Created transformation node
        """
        # Validate input nodes exist
        for node_id in input_nodes:
            if not self.graph.get_node(node_id):
                raise ValueError(f"Input node {node_id} not found")

        node = DataLineageNode(
            node_id=str(uuid.uuid4()),
            name=name,
            node_type="transformation",
            timestamp=datetime.now(pytz.UTC),
            metadata={"transformation_type": transformation_type, **(metadata or {})},
            parent_ids=input_nodes,
        )

        self.graph.add_node(node)

        # Create edges from input nodes
        for input_id in input_nodes:
            self.graph.add_edge(input_id, node.node_id)

        # Log the operation
        if self.audit_logger and actor:
            self.audit_logger.log_event(
                actor=actor,
                operation=OperationType.TRANSFORM,
                resource=f"lineage:node:{node.node_id}",
                details={
                    "action": "create_transformation_node",
                    "node_name": name,
                    "transformation_type": transformation_type,
                    "input_nodes": input_nodes,
                },
            )

        return node

    def create_destination_node(
        self,
        name: str,
        input_nodes: List[str],
        destination_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        actor: Optional[str] = None,
    ) -> DataLineageNode:
        """Create a destination node in the lineage graph.

        Args:
            name: Name of the destination
            input_nodes: List of input node IDs
            destination_type: Type of destination (database, file, etc.)
            metadata: Additional metadata about the destination
            actor: User creating the destination

        Returns:
            Created destination node
        """
        # Validate input nodes exist
        for node_id in input_nodes:
            if not self.graph.get_node(node_id):
                raise ValueError(f"Input node {node_id} not found")

        node = DataLineageNode(
            node_id=str(uuid.uuid4()),
            name=name,
            node_type="destination",
            timestamp=datetime.now(pytz.UTC),
            metadata={"destination_type": destination_type, **(metadata or {})},
            parent_ids=input_nodes,
        )

        self.graph.add_node(node)

        # Create edges from input nodes
        for input_id in input_nodes:
            self.graph.add_edge(input_id, node.node_id)

        # Log the operation
        if self.audit_logger and actor:
            self.audit_logger.log_event(
                actor=actor,
                operation=OperationType.WRITE,
                resource=f"lineage:node:{node.node_id}",
                details={
                    "action": "create_destination_node",
                    "node_name": name,
                    "destination_type": destination_type,
                    "input_nodes": input_nodes,
                },
            )

        return node

    def start_transformation(
        self,
        transformation_id: str,
        input_nodes: List[str],
        transformation_type: str,
        actor: str,
    ) -> None:
        """Start tracking a transformation operation.

        Args:
            transformation_id: Unique ID for the transformation
            input_nodes: List of input node IDs
            transformation_type: Type of transformation
            actor: User performing the transformation
        """
        if transformation_id in self._active_transformations:
            raise ValueError(f"Transformation {transformation_id} already active")

        self._active_transformations[transformation_id] = {
            "start_time": datetime.now(pytz.UTC),
            "input_nodes": input_nodes,
            "transformation_type": transformation_type,
            "actor": actor,
            "operations": [],
        }

        # Log the start
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=actor,
                operation=OperationType.TRANSFORM,
                resource=f"transformation:{transformation_id}",
                details={
                    "action": "start_transformation",
                    "transformation_type": transformation_type,
                    "input_nodes": input_nodes,
                },
            )

    def record_transformation_operation(
        self, transformation_id: str, operation: str, details: Dict[str, Any]
    ) -> None:
        """Record an operation within an active transformation.

        Args:
            transformation_id: ID of the active transformation
            operation: Description of the operation
            details: Operation details
        """
        if transformation_id not in self._active_transformations:
            raise ValueError(f"Transformation {transformation_id} not active")

        self._active_transformations[transformation_id]["operations"].append(
            {
                "timestamp": datetime.now(pytz.UTC).isoformat(),
                "operation": operation,
                "details": details,
            }
        )

    def complete_transformation(
        self,
        transformation_id: str,
        output_name: str,
        output_metadata: Optional[Dict[str, Any]] = None,
    ) -> DataLineageNode:
        """Complete a transformation and create the output node.

        Args:
            transformation_id: ID of the transformation to complete
            output_name: Name for the output node
            output_metadata: Additional metadata for the output

        Returns:
            Created output node
        """
        if transformation_id not in self._active_transformations:
            raise ValueError(f"Transformation {transformation_id} not active")

        transform_data = self._active_transformations[transformation_id]

        # Create transformation node with all recorded operations
        node = self.create_transformation_node(
            name=output_name,
            input_nodes=transform_data["input_nodes"],
            transformation_type=transform_data["transformation_type"],
            metadata={
                "transformation_id": transformation_id,
                "start_time": transform_data["start_time"].isoformat(),
                "end_time": datetime.now(pytz.UTC).isoformat(),
                "operations": transform_data["operations"],
                **(output_metadata or {}),
            },
            actor=transform_data["actor"],
        )

        # Clean up active transformation
        del self._active_transformations[transformation_id]

        # Log completion
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=transform_data["actor"],
                operation=OperationType.TRANSFORM,
                resource=f"transformation:{transformation_id}",
                details={
                    "action": "complete_transformation",
                    "output_node": node.node_id,
                    "output_name": output_name,
                },
            )

        return node

    def get_node_lineage(self, node_id: str) -> Dict[str, Any]:
        """Get complete lineage information for a node.

        Args:
            node_id: ID of the node

        Returns:
            Dictionary with lineage information
        """
        node = self.graph.get_node(node_id)
        if not node:
            return {"error": "Node not found"}

        ancestors = self.graph.get_ancestors(node_id)
        descendants = self.graph.get_descendants(node_id)

        # Get all ancestor nodes
        ancestor_nodes = []
        for ancestor_id in ancestors:
            ancestor = self.graph.get_node(ancestor_id)
            if ancestor:
                ancestor_nodes.append(
                    {
                        "node_id": ancestor.node_id,
                        "name": ancestor.name,
                        "type": ancestor.node_type,
                        "timestamp": ancestor.timestamp.isoformat(),
                    }
                )

        # Get all descendant nodes
        descendant_nodes = []
        for descendant_id in descendants:
            descendant = self.graph.get_node(descendant_id)
            if descendant:
                descendant_nodes.append(
                    {
                        "node_id": descendant.node_id,
                        "name": descendant.name,
                        "type": descendant.node_type,
                        "timestamp": descendant.timestamp.isoformat(),
                    }
                )

        return {
            "node": {
                "node_id": node.node_id,
                "name": node.name,
                "type": node.node_type,
                "timestamp": node.timestamp.isoformat(),
                "metadata": node.metadata,
            },
            "ancestors": ancestor_nodes,
            "descendants": descendant_nodes,
            "direct_parents": node.parent_ids,
            "direct_children": node.child_ids,
            "impact_analysis": self.graph.get_impact_analysis(node_id),
        }

    def find_data_sources(self, destination_id: str) -> List[str]:
        """Find all original data sources for a destination node.

        Args:
            destination_id: ID of the destination node

        Returns:
            List of source node IDs
        """
        ancestors = self.graph.get_ancestors(destination_id)
        sources = []

        for ancestor_id in ancestors:
            node = self.graph.get_node(ancestor_id)
            if node and node.node_type == "source":
                sources.append(ancestor_id)

        return sources

    def validate_lineage_completeness(self) -> Dict[str, Any]:
        """Validate that all nodes have complete lineage information.

        Returns:
            Validation results
        """
        issues = []

        for node_id in self.graph.graph.nodes():
            node = self.graph.get_node(node_id)
            if not node:
                issues.append({"node_id": node_id, "issue": "Missing node metadata"})
                continue

            # Check source nodes have no parents
            if node.node_type == "source" and node.parent_ids:
                issues.append({"node_id": node_id, "issue": "Source node has parents"})

            # Check non-source nodes have parents
            if node.node_type != "source" and not node.parent_ids:
                issues.append(
                    {"node_id": node_id, "issue": "Non-source node has no parents"}
                )

            # Check for orphaned nodes
            if node.node_type != "source" and not any(
                self.graph.get_node(pid) for pid in node.parent_ids
            ):
                issues.append(
                    {"node_id": node_id, "issue": "Node has invalid parent references"}
                )

        # Check for cycles
        cycles = self.graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                issues.append({"nodes": cycle, "issue": "Circular dependency detected"})

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "total_nodes": len(self.graph.graph.nodes()),
            "cycles_detected": len(cycles) if cycles else 0,
        }

    def export_lineage(self) -> Dict[str, Any]:
        """Export the complete lineage graph.

        Returns:
            Dictionary representation of the lineage graph
        """
        return self.graph.export_to_dict()

    def import_lineage(self, data: Dict[str, Any]) -> None:
        """Import a lineage graph.

        Args:
            data: Dictionary representation of the lineage graph
        """
        self.graph.import_from_dict(data)
