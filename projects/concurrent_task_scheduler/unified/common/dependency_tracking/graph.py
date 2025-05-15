"""
Dependency graph implementation for the unified concurrent task scheduler.

This module provides a graph-based implementation for tracking dependencies
between jobs and stages that can be used by both the render farm manager
and scientific computing implementations.
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum

try:
    import networkx as nx
except ImportError:
    # Fallback implementation for environments without networkx
    nx = None

from common.core.models import (
    Dependency,
    DependencyState,
    DependencyType,
    JobStatus,
    Result,
)
from common.core.utils import DateTimeEncoder, datetime_decoder

logger = logging.getLogger(__name__)


class GraphNodeType(str, Enum):
    """Types of nodes in a dependency graph."""
    
    JOB = "job"
    STAGE = "stage"
    GROUP = "group"
    RESOURCE = "resource"
    SIMULATION = "simulation"
    EXTERNAL = "external"


class DependencyNode:
    """A node in the dependency graph."""
    
    def __init__(self, node_id: str, node_type: GraphNodeType = GraphNodeType.JOB, metadata: Optional[Dict] = None):
        """
        Initialize a dependency node.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node
            metadata: Optional metadata for the node
        """
        self.id = node_id
        self.node_type = node_type
        self.metadata = metadata or {}


class DependencyGraph:
    """
    A graph-based implementation for tracking dependencies.
    
    The graph can be used to represent dependencies between jobs, stages,
    or any other entities that have dependency relationships.
    """
    
    def __init__(self, owner_id: str):
        """
        Initialize a dependency graph.
        
        Args:
            owner_id: ID of the owner (job, simulation, etc.) of this graph
        """
        self.owner_id = owner_id
        self.nodes: Dict[str, DependencyNode] = {}
        self.dependencies: Dict[Tuple[str, str], Dependency] = {}
        
        # Initialize the graph based on available libraries
        if nx is not None:
            self.graph = nx.DiGraph()
        else:
            # Fallback implementation using dictionaries
            self.adjacency_list: Dict[str, Set[str]] = {}
            self.reverse_adjacency_list: Dict[str, Set[str]] = {}
    
    def add_node(self, node_id: str, node_type: GraphNodeType = GraphNodeType.JOB, metadata: Optional[Dict] = None) -> None:
        """
        Add a node to the graph.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node
            metadata: Optional metadata for the node
        """
        if node_id in self.nodes:
            # Update existing node
            self.nodes[node_id].node_type = node_type
            if metadata:
                self.nodes[node_id].metadata.update(metadata)
            return
            
        # Create a new node
        node = DependencyNode(node_id, node_type, metadata)
        self.nodes[node_id] = node
        
        # Add to graph
        if nx is not None:
            self.graph.add_node(node_id, type=node_type, metadata=metadata or {})
        else:
            # Initialize adjacency list entries
            if node_id not in self.adjacency_list:
                self.adjacency_list[node_id] = set()
            if node_id not in self.reverse_adjacency_list:
                self.reverse_adjacency_list[node_id] = set()
    
    def add_dependency(
        self, 
        from_id: str, 
        to_id: str, 
        dependency_type: DependencyType = DependencyType.SEQUENTIAL,
        condition: Optional[str] = None,
    ) -> Result[bool]:
        """
        Add a dependency between two nodes.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            dependency_type: Type of dependency
            condition: Optional condition for the dependency
            
        Returns:
            Result with success status or error
        """
        # Add nodes if they don't exist
        if from_id not in self.nodes:
            self.add_node(from_id)
        if to_id not in self.nodes:
            self.add_node(to_id)
        
        # Check for cycles before adding the edge
        if self._would_create_cycle(from_id, to_id):
            return Result.err(f"Cannot add dependency from {from_id} to {to_id} because it would create a cycle")
        
        # Create dependency
        key = (from_id, to_id)
        dependency = Dependency(
            from_id=from_id,
            to_id=to_id,
            dependency_type=dependency_type,
            state=DependencyState.PENDING,
            condition=condition,
        )
        self.dependencies[key] = dependency
        
        # Add to graph
        if nx is not None:
            self.graph.add_edge(
                from_id, 
                to_id, 
                type=dependency_type, 
                state=DependencyState.PENDING,
                condition=condition,
            )
        else:
            # Update adjacency lists
            self.adjacency_list[from_id].add(to_id)
            self.reverse_adjacency_list[to_id].add(from_id)
        
        return Result.ok(True)
    
    def remove_dependency(self, from_id: str, to_id: str) -> Result[bool]:
        """
        Remove a dependency between two nodes.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            Result with success status or error
        """
        key = (from_id, to_id)
        if key not in self.dependencies:
            return Result.err(f"No dependency exists from {from_id} to {to_id}")
        
        # Remove from dependencies
        del self.dependencies[key]
        
        # Remove from graph
        if nx is not None:
            if self.graph.has_edge(from_id, to_id):
                self.graph.remove_edge(from_id, to_id)
        else:
            # Update adjacency lists
            if from_id in self.adjacency_list:
                self.adjacency_list[from_id].discard(to_id)
            if to_id in self.reverse_adjacency_list:
                self.reverse_adjacency_list[to_id].discard(from_id)
        
        return Result.ok(True)
    
    def get_dependency(self, from_id: str, to_id: str) -> Optional[Dependency]:
        """
        Get the dependency between two nodes.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            The dependency if it exists, None otherwise
        """
        key = (from_id, to_id)
        return self.dependencies.get(key)
    
    def get_dependencies_from(self, node_id: str) -> List[Dependency]:
        """
        Get all dependencies that originate from a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of dependencies
        """
        return [dep for (from_id, to_id), dep in self.dependencies.items() if from_id == node_id]
    
    def get_dependencies_to(self, node_id: str) -> List[Dependency]:
        """
        Get all dependencies that target a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of dependencies
        """
        return [dep for (from_id, to_id), dep in self.dependencies.items() if to_id == node_id]
    
    def update_dependency_state(
        self, from_id: str, to_id: str, state: DependencyState
    ) -> Optional[Dependency]:
        """
        Update the state of a dependency.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            state: New state for the dependency
            
        Returns:
            The updated dependency if it exists, None otherwise
        """
        key = (from_id, to_id)
        if key not in self.dependencies:
            return None
        
        # Update dependency state
        dependency = self.dependencies[key]
        dependency.state = state
        
        # Update graph
        if nx is not None:
            self.graph[from_id][to_id]['state'] = state
        
        return dependency
    
    def satisfy_dependency(self, from_id: str, to_id: str) -> Optional[Dependency]:
        """
        Mark a dependency as satisfied.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            The updated dependency if it exists, None otherwise
        """
        return self.update_dependency_state(from_id, to_id, DependencyState.SATISFIED)
    
    def bypass_dependency(self, from_id: str, to_id: str) -> Optional[Dependency]:
        """
        Bypass a dependency (mark as satisfied without the normal conditions).
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            The updated dependency if it exists, None otherwise
        """
        return self.update_dependency_state(from_id, to_id, DependencyState.BYPASSED)
    
    def fail_dependency(self, from_id: str, to_id: str) -> Optional[Dependency]:
        """
        Mark a dependency as failed.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            The updated dependency if it exists, None otherwise
        """
        return self.update_dependency_state(from_id, to_id, DependencyState.FAILED)
    
    def update_node_status(self, node_id: str, status: Union[JobStatus, str]) -> List[str]:
        """
        Update a node's status and propagate changes through the graph.
        
        This method is typically called when a job/stage status changes,
        and it updates the dependencies accordingly.
        
        Args:
            node_id: ID of the node
            status: New status for the node
            
        Returns:
            List of affected node IDs
        """
        if node_id not in self.nodes:
            return []
        
        # Store status in node metadata
        self.nodes[node_id].metadata['status'] = status
        
        affected_nodes = []
        
        # If the node is completed, satisfy all outgoing dependencies
        if isinstance(status, str):
            if not isinstance(status, JobStatus):
                # Convert string to JobStatus if possible
                try:
                    status = JobStatus(status)
                except ValueError:
                    # If it's not a valid JobStatus, just check the string
                    is_completed = status.lower() == "completed"
            else:
                is_completed = status == JobStatus.COMPLETED
        else:
            is_completed = status == JobStatus.COMPLETED
            
        if is_completed:
            # Get all outgoing dependencies
            dependencies = self.get_dependencies_from(node_id)
            
            # Satisfy each dependency
            for dependency in dependencies:
                self.satisfy_dependency(dependency.from_id, dependency.to_id)
                affected_nodes.append(dependency.to_id)
        
        return affected_nodes
    
    def are_all_dependencies_satisfied(self, node_id: str) -> bool:
        """
        Check if all dependencies to a node are satisfied.
        
        Args:
            node_id: ID of the node
            
        Returns:
            True if all dependencies are satisfied or bypassed, False otherwise
        """
        dependencies = self.get_dependencies_to(node_id)
        
        if not dependencies:
            # No dependencies means all are satisfied
            return True
        
        return all(dependency.is_satisfied() for dependency in dependencies)
    
    def is_node_blocked(self, node_id: str, completed_nodes: Set[str]) -> Optional[List[str]]:
        """
        Check if a node is blocked by dependencies.
        
        Args:
            node_id: ID of the node
            completed_nodes: Set of completed node IDs
            
        Returns:
            List of blocking node IDs if the node is blocked, None otherwise
        """
        if node_id not in self.nodes:
            return None
        
        blocking_nodes = []
        dependencies = self.get_dependencies_to(node_id)
        
        for dependency in dependencies:
            if dependency.is_satisfied():
                continue
                
            if dependency.from_id in completed_nodes:
                # Dependency is completed but not satisfied - mark it as satisfied
                self.satisfy_dependency(dependency.from_id, dependency.to_id)
                continue
                
            blocking_nodes.append(dependency.from_id)
        
        return blocking_nodes if blocking_nodes else None
    
    def get_ready_nodes(self, completed_nodes: Set[str]) -> Set[str]:
        """
        Get all nodes that are ready to execute.
        
        Args:
            completed_nodes: Set of completed node IDs
            
        Returns:
            Set of node IDs that are ready to execute
        """
        ready_nodes = set()
        
        # Check each node
        for node_id in self.nodes:
            # Skip completed nodes
            if node_id in completed_nodes:
                continue
                
            # Check if all dependencies are satisfied
            if self.are_all_dependencies_satisfied(node_id):
                ready_nodes.add(node_id)
        
        return ready_nodes
    
    def get_root_nodes(self) -> List[str]:
        """
        Get all root nodes (nodes with no incoming dependencies).
        
        Returns:
            List of root node IDs
        """
        if nx is not None:
            return [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        else:
            return [n for n in self.nodes if not self.reverse_adjacency_list.get(n, set())]
    
    def get_leaf_nodes(self) -> List[str]:
        """
        Get all leaf nodes (nodes with no outgoing dependencies).
        
        Returns:
            List of leaf node IDs
        """
        if nx is not None:
            return [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        else:
            return [n for n in self.nodes if not self.adjacency_list.get(n, set())]
    
    def get_critical_path(self) -> List[str]:
        """
        Get the critical path through the graph.
        
        The critical path is the longest path through the graph,
        which represents the sequence of tasks that must be completed
        to minimize the total duration.
        
        Returns:
            List of node IDs in the critical path
        """
        if not nx:
            # Fallback implementation for environments without networkx
            # Perform a topological sort
            sorted_nodes = self._topological_sort()
            
            # Find the longest path
            distances = {node: 0 for node in self.nodes}
            predecessors = {node: None for node in self.nodes}
            
            for node in sorted_nodes:
                for successor in self.adjacency_list.get(node, set()):
                    if distances[successor] < distances[node] + 1:
                        distances[successor] = distances[node] + 1
                        predecessors[successor] = node
            
            # Find the node with the maximum distance
            end_node = max(distances, key=distances.get)
            
            # Reconstruct the path
            path = [end_node]
            while predecessors[path[0]] is not None:
                path.insert(0, predecessors[path[0]])
            
            return path
        
        try:
            # Use networkx's algorithm if available
            if len(self.graph.nodes()) <= 1:
                return list(self.graph.nodes())
            
            # Find longest path using topological sort
            path = nx.dag_longest_path(self.graph)
            return path
        except Exception as e:
            logger.error(f"Error computing critical path: {e}")
            return list(self.graph.nodes())
    
    def validate(self) -> List[str]:
        """
        Validate the graph for correctness.
        
        Returns:
            List of error messages, empty if graph is valid
        """
        errors = []
        
        # Check for cycles
        if self._has_cycles():
            errors.append("Dependency graph contains cycles")
        
        # Check for missing nodes
        for key, dependency in self.dependencies.items():
            from_id, to_id = key
            if from_id not in self.nodes:
                errors.append(f"Node {from_id} is used in a dependency but not defined")
            if to_id not in self.nodes:
                errors.append(f"Node {to_id} is used in a dependency but not defined")
        
        return errors
    
    def _has_cycles(self) -> bool:
        """
        Check if the graph has cycles.
        
        Returns:
            True if the graph has cycles, False otherwise
        """
        if nx is not None:
            try:
                # Use networkx's algorithm if available
                return not nx.is_directed_acyclic_graph(self.graph)
            except Exception:
                pass
        
        # Fallback implementation using DFS
        visited = set()
        rec_stack = set()
        
        def check_cycles(node):
            # Mark node as visited and add to recursion stack
            visited.add(node)
            rec_stack.add(node)
            
            # Visit all neighbors
            for neighbor in self.adjacency_list.get(node, set()):
                if neighbor not in visited:
                    if check_cycles(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            # Remove from recursion stack
            rec_stack.remove(node)
            return False
        
        # Check each unvisited node
        for node in self.nodes:
            if node not in visited:
                if check_cycles(node):
                    return True
        
        return False
    
    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """
        Check if adding an edge would create a cycle.
        
        Args:
            from_id: ID of the prerequisite node
            to_id: ID of the dependent node
            
        Returns:
            True if adding the edge would create a cycle, False otherwise
        """
        if from_id == to_id:
            # Self-dependency is a cycle
            return True
        
        if nx is not None:
            # Use networkx's algorithm if available
            try:
                # Add the edge temporarily
                self.graph.add_edge(from_id, to_id)
                
                # Check for cycles
                has_cycle = not nx.is_directed_acyclic_graph(self.graph)
                
                # Remove the edge
                self.graph.remove_edge(from_id, to_id)
                
                return has_cycle
            except Exception:
                # If there's an error, remove the edge and use the fallback
                try:
                    self.graph.remove_edge(from_id, to_id)
                except Exception:
                    pass
        
        # Fallback implementation using DFS
        # Check if there's a path from to_id to from_id
        visited = set()
        
        def dfs(node):
            if node == from_id:
                return True
            
            visited.add(node)
            
            for neighbor in self.adjacency_list.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
            
            return False
        
        return dfs(to_id)
    
    def _topological_sort(self) -> List[str]:
        """
        Perform a topological sort of the graph.
        
        Returns:
            List of nodes in topological order
        """
        if nx is not None:
            try:
                # Use networkx's algorithm if available
                return list(nx.topological_sort(self.graph))
            except Exception:
                pass
        
        # Fallback implementation of topological sort
        visited = set()
        temp_mark = set()
        order = []
        
        def visit(node):
            if node in temp_mark:
                # Cycle detected
                return
            
            if node not in visited:
                temp_mark.add(node)
                
                # Visit successors
                for successor in self.adjacency_list.get(node, set()):
                    visit(successor)
                
                temp_mark.remove(node)
                visited.add(node)
                order.insert(0, node)
        
        # Visit each unvisited node
        for node in self.nodes:
            if node not in visited:
                visit(node)
        
        return order
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the graph to a dictionary.
        
        Returns:
            Dictionary representation of the graph
        """
        # Serialize nodes
        nodes = {
            node_id: {
                "type": node.node_type,
                "metadata": node.metadata
            }
            for node_id, node in self.nodes.items()
        }
        
        # Serialize edges
        edges = [
            {
                "from": from_id,
                "to": to_id,
                "type": dependency.dependency_type,
                "state": dependency.state,
                "condition": dependency.condition
            }
            for (from_id, to_id), dependency in self.dependencies.items()
        ]
        
        return {
            "owner_id": self.owner_id,
            "nodes": nodes,
            "edges": edges
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """
        Create a graph from a serialized dictionary.
        
        Args:
            data: Dictionary representation of the graph
            
        Returns:
            The deserialized graph
        """
        # Create a new graph
        graph = cls(data["owner_id"])
        
        # Add nodes
        for node_id, node_data in data["nodes"].items():
            graph.add_node(
                node_id,
                node_data.get("type", GraphNodeType.JOB),
                node_data.get("metadata", {})
            )
        
        # Add edges
        for edge in data["edges"]:
            graph.add_dependency(
                edge["from"],
                edge["to"],
                edge.get("type", DependencyType.SEQUENTIAL),
                edge.get("condition")
            )
            
            # Set edge state
            if "state" in edge and edge["state"] != DependencyState.PENDING:
                graph.update_dependency_state(edge["from"], edge["to"], edge["state"])
        
        return graph