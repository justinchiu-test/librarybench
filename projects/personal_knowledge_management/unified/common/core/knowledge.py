"""Knowledge management system for the unified personal knowledge management system."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

# Import networkx with version compatibility for Python 3.8
try:
    import networkx as nx
except ImportError:
    # Fall back to a minimal implementation if networkx is not available
    class MinimalGraph:
        """Minimal implementation of a graph for testing purposes."""
        def __init__(self):
            self.nodes = {}
            self.edges = {}
            
        def add_node(self, node_id, **attrs):
            self.nodes[node_id] = attrs
            
        def add_edge(self, source, target, **attrs):
            if (source, target) not in self.edges:
                self.edges[(source, target)] = attrs
                
        def has_node(self, node_id):
            return node_id in self.nodes
            
        def has_edge(self, source, target):
            return (source, target) in self.edges
            
        def clear(self):
            self.nodes.clear()
            self.edges.clear()
            
        def nodes(self, data=True):
            if data:
                return list(self.nodes.items())
            return list(self.nodes.keys())
            
        def edges(self, data=True):
            if data:
                return [(s, t, d) for (s, t), d in self.edges.items()]
            return [(s, t) for s, t in self.edges.keys()]
    
    # Use the minimal graph implementation
    class nx:
        DiGraph = MinimalGraph
        NetworkXNoPath = Exception
        NodeNotFound = Exception
        
        @staticmethod
        def all_simple_paths(graph, source, target, cutoff=None):
            """Minimal implementation of all_simple_paths for compatibility."""
            if not graph.has_node(source) or not graph.has_node(target):
                return []
            return [[source, target]]

from common.core.models import KnowledgeNode, NodeType, Relation, RelationType
from common.core.storage import BaseStorage

T = TypeVar('T', bound=KnowledgeNode)


class KnowledgeBase(ABC):
    """Abstract base class for knowledge management system."""
    
    @abstractmethod
    def __init__(self, storage: BaseStorage):
        """Initialize with a storage implementation."""
        pass
    
    @abstractmethod
    def add_node(self, node: KnowledgeNode) -> UUID:
        """Add a knowledge node to the system."""
        pass
    
    @abstractmethod
    def get_node(self, node_id: UUID, node_type: Optional[Type[T]] = None) -> Optional[KnowledgeNode]:
        """Get a knowledge node by ID."""
        pass
    
    @abstractmethod
    def update_node(self, node: KnowledgeNode) -> bool:
        """Update a knowledge node."""
        pass
    
    @abstractmethod
    def delete_node(self, node_id: UUID, node_type: Optional[Type[T]] = None) -> bool:
        """Delete a knowledge node."""
        pass
    
    @abstractmethod
    def link_nodes(self, source_id: UUID, target_id: UUID, relation_type: Union[RelationType, str], 
                 metadata: Optional[Dict[str, Any]] = None) -> Relation:
        """Create a relationship between two nodes."""
        pass
    
    @abstractmethod
    def get_related_nodes(self, node_id: UUID, relation_types: Optional[List[Union[RelationType, str]]] = None,
                        direction: str = "both") -> Dict[str, List[KnowledgeNode]]:
        """Get nodes related to a specific knowledge node."""
        pass
    
    @abstractmethod
    def search(self, query: str, node_types: Optional[List[Type[T]]] = None) -> Dict[str, List[KnowledgeNode]]:
        """Search for knowledge nodes containing a specific text."""
        pass


class KnowledgeGraph:
    """Manages a graph representation of knowledge nodes and their relationships."""
    
    def __init__(self):
        """Initialize an empty knowledge graph."""
        self._graph = nx.DiGraph()
        
    def add_node(self, node_id: str, **attrs):
        """Add a node to the graph.
        
        Args:
            node_id: ID of the node to add.
            **attrs: Attributes to associate with the node.
        """
        self._graph.add_node(node_id, **attrs)
        
    def add_edge(self, source_id: str, target_id: str, **attrs):
        """Add an edge to the graph.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            **attrs: Attributes to associate with the edge.
        """
        self._graph.add_edge(source_id, target_id, **attrs)
        
    def remove_node(self, node_id: str):
        """Remove a node from the graph.
        
        Args:
            node_id: ID of the node to remove.
        """
        if self._graph.has_node(node_id):
            self._graph.remove_node(node_id)
            
    def remove_edge(self, source_id: str, target_id: str):
        """Remove an edge from the graph.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
        """
        if self._graph.has_edge(source_id, target_id):
            self._graph.remove_edge(source_id, target_id)
            
    def get_neighbors(self, node_id: str, direction: str = "both") -> Dict[str, List[str]]:
        """Get neighbors of a node.
        
        Args:
            node_id: ID of the node.
            direction: Direction of relationships to consider ("out", "in", or "both").
            
        Returns:
            Dictionary mapping relation types to lists of neighbor node IDs.
        """
        if not self._graph.has_node(node_id):
            return {}
            
        neighbors = {}
        
        # Get outgoing edges (relations from this node to others)
        if direction in ["out", "both"]:
            for source, target, data in self._graph.out_edges(node_id, data=True):
                relation_type = data.get('type', 'unknown')
                if relation_type not in neighbors:
                    neighbors[relation_type] = []
                neighbors[relation_type].append(target)
                
        # Get incoming edges (relations from others to this node)
        if direction in ["in", "both"]:
            for source, target, data in self._graph.in_edges(node_id, data=True):
                relation_type = f"incoming_{data.get('type', 'unknown')}"
                if relation_type not in neighbors:
                    neighbors[relation_type] = []
                neighbors[relation_type].append(source)
                
        return neighbors
    
    def get_nodes_by_type(self, node_type: str) -> List[str]:
        """Get all nodes of a specific type.
        
        Args:
            node_type: Type of nodes to get.
            
        Returns:
            List of node IDs.
        """
        return [n for n, attrs in self._graph.nodes(data=True) if attrs.get('type') == node_type]
        
    def get_node_attributes(self, node_id: str) -> Dict[str, Any]:
        """Get all attributes of a node.
        
        Args:
            node_id: ID of the node.
            
        Returns:
            Dictionary of node attributes.
        """
        if not self._graph.has_node(node_id):
            return {}
        return dict(self._graph.nodes[node_id])
        
    def get_edge_attributes(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Get all attributes of an edge.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            
        Returns:
            Dictionary of edge attributes.
        """
        if not self._graph.has_edge(source_id, target_id):
            return {}
        return dict(self._graph.edges[source_id, target_id])
        
    def has_node(self, node_id: str) -> bool:
        """Check if the graph has a specific node.
        
        Args:
            node_id: ID of the node to check.
            
        Returns:
            True if the node exists, False otherwise.
        """
        return self._graph.has_node(node_id)
        
    def has_edge(self, source_id: str, target_id: str) -> bool:
        """Check if the graph has a specific edge.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            
        Returns:
            True if the edge exists, False otherwise.
        """
        return self._graph.has_edge(source_id, target_id)
        
    def find_path(self, source_id: str, target_id: str, cutoff: Optional[int] = None) -> List[List[str]]:
        """Find all paths between two nodes.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            cutoff: Maximum path length to consider.
            
        Returns:
            List of paths, where each path is a list of node IDs.
        """
        if not self._graph.has_node(source_id) or not self._graph.has_node(target_id):
            return []
            
        try:
            paths = list(nx.all_simple_paths(self._graph, source_id, target_id, cutoff=cutoff))
            return paths
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
            
    def export_to_json(self, file_path: Union[str, Path]) -> None:
        """Export the graph to a JSON file.
        
        Args:
            file_path: Path to save the JSON file.
        """
        # Convert the graph to a serializable format
        data = {
            'nodes': [],
            'edges': []
        }
        
        # Export nodes with their attributes
        for node_id, attrs in self._graph.nodes(data=True):
            node_data = {'id': node_id}
            node_data.update(attrs)
            data['nodes'].append(node_data)
            
        # Export edges with their attributes
        for source, target, attrs in self._graph.edges(data=True):
            edge_data = {
                'source': source,
                'target': target
            }
            edge_data.update(attrs)
            data['edges'].append(edge_data)
            
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    def import_from_json(self, file_path: Union[str, Path]) -> None:
        """Import the graph from a JSON file.
        
        Args:
            file_path: Path to the JSON file.
        """
        # Clear the current graph
        self._graph.clear()
        
        # Read from file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Import nodes with their attributes
        for node_data in data.get('nodes', []):
            node_id = node_data.pop('id')
            self._graph.add_node(node_id, **node_data)
            
        # Import edges with their attributes
        for edge_data in data.get('edges', []):
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            self._graph.add_edge(source, target, **edge_data)


class StandardKnowledgeBase(KnowledgeBase):
    """Standard implementation of the knowledge management system."""
    
    def __init__(self, storage: BaseStorage):
        """Initialize with a storage implementation.
        
        Args:
            storage: Storage system to use.
        """
        self.storage = storage
        self.graph = KnowledgeGraph()
        self._build_knowledge_graph()
        
    def _build_knowledge_graph(self) -> None:
        """Build the knowledge graph from the storage system."""
        # This is a simplified implementation. In a real system, you would:
        # 1. Load all nodes from storage
        # 2. Add them to the graph
        # 3. Load all relations from storage
        # 4. Add them to the graph
        
        # For now, we'll have an empty graph to start
        pass
        
    def add_node(self, node: KnowledgeNode) -> UUID:
        """Add a knowledge node to the system.
        
        Args:
            node: The node to add.
            
        Returns:
            ID of the added node.
        """
        # Save the node to storage
        self.storage.save(node)
        
        # Add to the graph
        node_type = type(node).__name__
        self.graph.add_node(str(node.id), type=node_type, title=getattr(node, 'title', ''))
        
        return node.id
        
    def get_node(self, node_id: UUID, node_type: Optional[Type[T]] = None) -> Optional[KnowledgeNode]:
        """Get a knowledge node by ID.
        
        Args:
            node_id: ID of the node to get.
            node_type: Optional type of the node to get.
            
        Returns:
            The requested node if found, None otherwise.
        """
        if node_type is not None:
            return self.storage.get(node_type, node_id)
            
        # If node_type is not specified, try to determine it from the graph
        if self.graph.has_node(str(node_id)):
            attrs = self.graph.get_node_attributes(str(node_id))
            node_type_name = attrs.get('type')
            
            if node_type_name:
                # This is just a placeholder. In a real implementation, you would
                # have a registry of node types mapped to their class names.
                # For now, we'll just try a few common types
                from common.core.models import Annotation
                
                if node_type_name == 'Annotation':
                    return self.storage.get(Annotation, node_id)
        
        return None
        
    def update_node(self, node: KnowledgeNode) -> bool:
        """Update a knowledge node.
        
        Args:
            node: The node to update.
            
        Returns:
            True if the node was updated, False otherwise.
        """
        # Update the node in storage
        node.update()  # Update the timestamp
        self.storage.save(node)
        
        # Update the graph
        node_type = type(node).__name__
        self.graph.add_node(str(node.id), type=node_type, title=getattr(node, 'title', ''))
        
        return True
        
    def delete_node(self, node_id: UUID, node_type: Optional[Type[T]] = None) -> bool:
        """Delete a knowledge node.
        
        Args:
            node_id: ID of the node to delete.
            node_type: Optional type of the node to delete.
            
        Returns:
            True if the node was deleted, False otherwise.
        """
        if node_type is None:
            # If node_type is not specified, try to determine it from the graph
            if self.graph.has_node(str(node_id)):
                attrs = self.graph.get_node_attributes(str(node_id))
                node_type_name = attrs.get('type')
                
                if node_type_name:
                    # This is just a placeholder. In a real implementation, you would
                    # have a registry of node types mapped to their class names.
                    from common.core.models import Annotation
                    
                    if node_type_name == 'Annotation':
                        node_type = Annotation
        
        if node_type is None:
            # If we still don't know the node type, we can't delete it
            return False
            
        # Delete the node from storage
        result = self.storage.delete(node_type, node_id)
        
        # Delete from the graph
        if result:
            self.graph.remove_node(str(node_id))
            
        return result
        
    def link_nodes(self, source_id: UUID, target_id: UUID, relation_type: Union[RelationType, str], 
                 metadata: Optional[Dict[str, Any]] = None) -> Relation:
        """Create a relationship between two nodes.
        
        Args:
            source_id: ID of the source node.
            target_id: ID of the target node.
            relation_type: Type of the relation.
            metadata: Optional metadata for the relation.
            
        Returns:
            The created relation.
        """
        # Create the relation object
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            metadata=metadata or {}
        )
        
        # In a real implementation, you would save the relation to storage
        # For now, we'll just add it to the graph
        relation_type_str = relation_type.value if isinstance(relation_type, RelationType) else relation_type
        self.graph.add_edge(str(source_id), str(target_id), type=relation_type_str, metadata=metadata or {})
        
        return relation
        
    def get_related_nodes(self, node_id: UUID, relation_types: Optional[List[Union[RelationType, str]]] = None,
                        direction: str = "both") -> Dict[str, List[KnowledgeNode]]:
        """Get nodes related to a specific knowledge node.
        
        Args:
            node_id: ID of the node.
            relation_types: Optional list of relation types to include.
            direction: Direction of relationships to consider ("out", "in", or "both").
            
        Returns:
            Dictionary mapping relation types to lists of related nodes.
        """
        # Convert relation types to strings if needed
        relation_type_strs = None
        if relation_types:
            relation_type_strs = [r.value if isinstance(r, RelationType) else r for r in relation_types]
            
        # Get neighbor IDs from the graph
        neighbors = self.graph.get_neighbors(str(node_id), direction)
        
        # Filter by relation types if specified
        if relation_type_strs:
            neighbors = {k: v for k, v in neighbors.items() if k in relation_type_strs}
            
        # Load the actual nodes from storage
        result = {}
        for relation_type, neighbor_ids in neighbors.items():
            result[relation_type] = []
            
            for neighbor_id in neighbor_ids:
                node = self.get_node(UUID(neighbor_id))
                if node:
                    result[relation_type].append(node)
                    
        return result
        
    def search(self, query: str, node_types: Optional[List[Type[T]]] = None) -> Dict[str, List[KnowledgeNode]]:
        """Search for knowledge nodes containing a specific text.
        
        Args:
            query: The search query.
            node_types: Optional list of node types to search.
            
        Returns:
            Dictionary mapping node types to lists of matching nodes.
        """
        results = {}
        
        # If no node types specified, use a default set
        if not node_types:
            from common.core.models import Annotation
            node_types = [Annotation]  # This is just a placeholder
            
        # Search each node type
        for node_type in node_types:
            type_name = node_type.__name__
            matches = self.storage.search_text(node_type, query, ['title', 'content'])
            
            if matches:
                results[type_name] = matches
                
        return results