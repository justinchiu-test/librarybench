"""Data lineage graph implementation."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import networkx as nx
from graphviz import Digraph

from pymigrate.models import DataLineageNode


class LineageGraph:
    """Manages the data lineage graph structure."""

    def __init__(self):
        """Initialize an empty lineage graph."""
        self.graph = nx.DiGraph()
        self._node_metadata: Dict[str, DataLineageNode] = {}

    def add_node(self, node: DataLineageNode) -> None:
        """Add a node to the lineage graph.

        Args:
            node: Lineage node to add
        """
        self.graph.add_node(node.node_id)
        self._node_metadata[node.node_id] = node

        # Add edges for parent relationships
        for parent_id in node.parent_ids:
            if parent_id in self.graph:
                self.graph.add_edge(parent_id, node.node_id)

        # Add edges for child relationships
        for child_id in node.child_ids:
            if child_id in self.graph:
                self.graph.add_edge(node.node_id, child_id)

    def add_edge(
        self, parent_id: str, child_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an edge between two nodes.

        Args:
            parent_id: ID of parent node
            child_id: ID of child node
            metadata: Optional edge metadata
        """
        if parent_id not in self.graph:
            raise ValueError(f"Parent node {parent_id} not found in graph")
        if child_id not in self.graph:
            raise ValueError(f"Child node {child_id} not found in graph")

        self.graph.add_edge(parent_id, child_id, metadata=metadata or {})

        # Update node relationships
        parent_node = self._node_metadata[parent_id]
        child_node = self._node_metadata[child_id]

        if child_id not in parent_node.child_ids:
            parent_node.child_ids.append(child_id)
        if parent_id not in child_node.parent_ids:
            child_node.parent_ids.append(parent_id)

    def get_node(self, node_id: str) -> Optional[DataLineageNode]:
        """Get a node by ID.

        Args:
            node_id: ID of node to retrieve

        Returns:
            Node if found, None otherwise
        """
        return self._node_metadata.get(node_id)

    def get_ancestors(self, node_id: str) -> Set[str]:
        """Get all ancestors of a node.

        Args:
            node_id: ID of node

        Returns:
            Set of ancestor node IDs
        """
        if node_id not in self.graph:
            return set()
        return nx.ancestors(self.graph, node_id)

    def get_descendants(self, node_id: str) -> Set[str]:
        """Get all descendants of a node.

        Args:
            node_id: ID of node

        Returns:
            Set of descendant node IDs
        """
        if node_id not in self.graph:
            return set()
        return nx.descendants(self.graph, node_id)

    def get_lineage_path(self, source_id: str, target_id: str) -> List[List[str]]:
        """Get all paths between two nodes.

        Args:
            source_id: ID of source node
            target_id: ID of target node

        Returns:
            List of paths (each path is a list of node IDs)
        """
        if source_id not in self.graph or target_id not in self.graph:
            return []

        try:
            return list(nx.all_simple_paths(self.graph, source_id, target_id))
        except nx.NetworkXNoPath:
            return []

    def get_impact_analysis(self, node_id: str) -> Dict[str, Any]:
        """Analyze the impact of changes to a node.

        Args:
            node_id: ID of node to analyze

        Returns:
            Dictionary with impact analysis results
        """
        if node_id not in self.graph:
            return {"error": "Node not found"}

        descendants = self.get_descendants(node_id)
        ancestors = self.get_ancestors(node_id)

        return {
            "node_id": node_id,
            "direct_children": list(self.graph.successors(node_id)),
            "direct_parents": list(self.graph.predecessors(node_id)),
            "all_descendants": list(descendants),
            "all_ancestors": list(ancestors),
            "downstream_impact_count": len(descendants),
            "upstream_dependencies_count": len(ancestors),
        }

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the lineage graph.

        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []

    def visualize(self, output_path: str, format: str = "png") -> None:
        """Generate a visual representation of the lineage graph.

        Args:
            output_path: Path to save the visualization
            format: Output format (png, pdf, svg, etc.)
        """
        dot = Digraph(comment="Data Lineage Graph")
        dot.attr(rankdir="LR")

        # Add nodes with metadata
        for node_id in self.graph.nodes():
            node = self._node_metadata[node_id]
            label = f"{node.name}\n({node.node_type})\n{node.timestamp.strftime('%Y-%m-%d %H:%M')}"

            # Color nodes by type
            if node.node_type == "source":
                dot.node(
                    node_id, label, shape="box", style="filled", fillcolor="lightblue"
                )
            elif node.node_type == "transformation":
                dot.node(
                    node_id,
                    label,
                    shape="diamond",
                    style="filled",
                    fillcolor="lightgreen",
                )
            elif node.node_type == "destination":
                dot.node(
                    node_id, label, shape="box", style="filled", fillcolor="lightcoral"
                )
            else:
                dot.node(node_id, label)

        # Add edges
        for parent_id, child_id in self.graph.edges():
            dot.edge(parent_id, child_id)

        # Render the graph
        dot.render(output_path, format=format, cleanup=True)

    def export_to_dict(self) -> Dict[str, Any]:
        """Export the lineage graph to a dictionary.

        Returns:
            Dictionary representation of the graph
        """
        nodes = []
        for node_id, node in self._node_metadata.items():
            nodes.append(
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "node_type": node.node_type,
                    "timestamp": node.timestamp.isoformat()
                    if hasattr(node.timestamp, "isoformat")
                    else str(node.timestamp),
                    "metadata": node.metadata,
                    "parent_ids": node.parent_ids,
                    "child_ids": node.child_ids,
                }
            )

        edges = []
        for parent_id, child_id, data in self.graph.edges(data=True):
            edges.append(
                {
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "metadata": data.get("metadata", {}),
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "source_nodes": len([n for n in nodes if n["node_type"] == "source"]),
                "transformation_nodes": len(
                    [n for n in nodes if n["node_type"] == "transformation"]
                ),
                "destination_nodes": len(
                    [n for n in nodes if n["node_type"] == "destination"]
                ),
            },
        }

    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """Import a lineage graph from a dictionary.

        Args:
            data: Dictionary representation of the graph
        """
        # Clear existing graph
        self.graph.clear()
        self._node_metadata.clear()

        # Add nodes
        for node_data in data["nodes"]:
            node = DataLineageNode(
                node_id=node_data["node_id"],
                name=node_data["name"],
                node_type=node_data["node_type"],
                timestamp=datetime.fromisoformat(node_data["timestamp"]),
                metadata=node_data["metadata"],
                parent_ids=node_data["parent_ids"],
                child_ids=node_data["child_ids"],
            )
            self.add_node(node)

        # Add edges
        for edge_data in data["edges"]:
            if (
                edge_data["parent_id"] in self.graph
                and edge_data["child_id"] in self.graph
            ):
                self.graph.add_edge(
                    edge_data["parent_id"],
                    edge_data["child_id"],
                    metadata=edge_data.get("metadata", {}),
                )
