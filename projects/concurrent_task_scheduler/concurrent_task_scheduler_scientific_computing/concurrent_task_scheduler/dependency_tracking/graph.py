"""Dependency graph implementation for simulation dependency tracking."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from concurrent_task_scheduler.models import (
    Result,
    Simulation,
    SimulationStage,
    SimulationStageStatus,
    SystemEvent,
)

logger = logging.getLogger(__name__)


class DependencyType(str, Enum):
    """Types of dependencies between simulation stages."""

    SEQUENTIAL = "sequential"  # B starts after A completes
    DATA = "data"  # B requires data produced by A
    RESOURCE = "resource"  # B requires resources used by A
    CONDITIONAL = "conditional"  # B starts only if A meets certain conditions
    TEMPORAL = "temporal"  # B starts at a specific time relative to A


class DependencyState(str, Enum):
    """States of a dependency between stages."""

    PENDING = "pending"  # Dependency not yet satisfied
    SATISFIED = "satisfied"  # Dependency has been satisfied
    FAILED = "failed"  # Dependency cannot be satisfied
    BYPASSED = "bypassed"  # Dependency was manually bypassed


class GraphNodeType(str, Enum):
    """Types of nodes in the dependency graph."""

    STAGE = "stage"  # A simulation stage
    JOIN = "join"  # A join point for multiple paths
    FORK = "fork"  # A fork point for parallel execution
    DECISION = "decision"  # A decision point
    START = "start"  # The start of a workflow
    END = "end"  # The end of a workflow


class SimulationDependency:
    """A dependency between simulation stages."""

    def __init__(
        self,
        from_stage_id: str,
        to_stage_id: str,
        dependency_type: DependencyType = DependencyType.SEQUENTIAL,
        condition: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        self.from_stage_id = from_stage_id
        self.to_stage_id = to_stage_id
        self.dependency_type = dependency_type
        self.condition = condition
        self.metadata = metadata or {}
        self.state = DependencyState.PENDING
        self.satisfaction_time = None
    
    def is_satisfied(self) -> bool:
        """Check if this dependency is satisfied."""
        return self.state == DependencyState.SATISFIED
    
    def satisfy(self) -> None:
        """Mark this dependency as satisfied."""
        from datetime import datetime
        
        self.state = DependencyState.SATISFIED
        self.satisfaction_time = datetime.now()
    
    def fail(self) -> None:
        """Mark this dependency as failed."""
        self.state = DependencyState.FAILED
    
    def bypass(self) -> None:
        """Manually bypass this dependency."""
        self.state = DependencyState.BYPASSED
    
    def reset(self) -> None:
        """Reset this dependency to pending state."""
        self.state = DependencyState.PENDING
        self.satisfaction_time = None


class DependencyGraph:
    """A graph representing dependencies between simulation stages."""

    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.graph = nx.DiGraph()
        self.dependencies: Dict[Tuple[str, str], SimulationDependency] = {}
        self.node_metadata: Dict[str, Dict[str, Union[str, dict]]] = {}
    
    def add_stage(
        self,
        stage_id: str,
        metadata: Optional[Dict[str, str]] = None,
        node_type: GraphNodeType = GraphNodeType.STAGE,
    ) -> None:
        """Add a stage to the dependency graph."""
        self.graph.add_node(stage_id, node_type=node_type)
        
        if metadata:
            self.node_metadata[stage_id] = metadata.copy()
    
    def add_dependency(
        self,
        from_stage_id: str,
        to_stage_id: str,
        dependency_type: DependencyType = DependencyType.SEQUENTIAL,
        condition: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Result[bool]:
        """Add a dependency between stages."""
        # Check if stages exist
        if from_stage_id not in self.graph:
            return Result.err(f"Stage {from_stage_id} does not exist in the graph")
        
        if to_stage_id not in self.graph:
            return Result.err(f"Stage {to_stage_id} does not exist in the graph")
        
        # Check for cycles
        if nx.has_path(self.graph, to_stage_id, from_stage_id):
            return Result.err(
                f"Adding dependency from {from_stage_id} to {to_stage_id} "
                f"would create a cycle"
            )
        
        # Create dependency
        dependency = SimulationDependency(
            from_stage_id=from_stage_id,
            to_stage_id=to_stage_id,
            dependency_type=dependency_type,
            condition=condition,
            metadata=metadata,
        )
        
        # Add to graph
        self.graph.add_edge(from_stage_id, to_stage_id,
                           type=dependency_type.value,
                           condition=condition)
        
        # Store dependency object
        edge_key = (from_stage_id, to_stage_id)
        self.dependencies[edge_key] = dependency
        
        return Result.ok(True)
    
    def remove_dependency(self, from_stage_id: str, to_stage_id: str) -> Result[bool]:
        """Remove a dependency from the graph."""
        edge_key = (from_stage_id, to_stage_id)
        
        if edge_key not in self.dependencies:
            return Result.err(f"Dependency from {from_stage_id} to {to_stage_id} does not exist")
        
        # Remove from graph
        self.graph.remove_edge(from_stage_id, to_stage_id)
        
        # Remove dependency object
        del self.dependencies[edge_key]
        
        return Result.ok(True)
    
    def get_dependency(
        self,
        from_stage_id: str,
        to_stage_id: str,
    ) -> Optional[SimulationDependency]:
        """Get a specific dependency."""
        edge_key = (from_stage_id, to_stage_id)
        return self.dependencies.get(edge_key)
    
    def get_dependencies_to(self, stage_id: str) -> List[SimulationDependency]:
        """Get all dependencies pointing to a stage."""
        return [
            dep for (from_id, to_id), dep in self.dependencies.items()
            if to_id == stage_id
        ]
    
    def get_dependencies_from(self, stage_id: str) -> List[SimulationDependency]:
        """Get all dependencies from a stage."""
        return [
            dep for (from_id, to_id), dep in self.dependencies.items()
            if from_id == stage_id
        ]
    
    def get_root_stages(self) -> List[str]:
        """Get all stages that have no incoming dependencies."""
        return [
            node for node in self.graph.nodes()
            if self.graph.in_degree(node) == 0
        ]
    
    def get_leaf_stages(self) -> List[str]:
        """Get all stages that have no outgoing dependencies."""
        return [
            node for node in self.graph.nodes()
            if self.graph.out_degree(node) == 0
        ]
    
    def get_ready_stages(self, completed_stages: Set[str]) -> List[str]:
        """Get all stages that are ready to execute."""
        result = []
        
        # Start with nodes that have no dependencies
        candidates = set(self.graph.nodes()) - completed_stages
        
        for stage_id in candidates:
            # Get dependencies
            dependencies = self.get_dependencies_to(stage_id)
            
            # Check if all dependencies are satisfied
            if all(
                dep.is_satisfied() or dep.from_stage_id in completed_stages
                for dep in dependencies
            ):
                result.append(stage_id)
        
        return result
    
    def are_all_dependencies_satisfied(self, stage_id: str) -> bool:
        """Check if all dependencies to a stage are satisfied."""
        dependencies = self.get_dependencies_to(stage_id)
        
        # If no dependencies, consider them satisfied
        if not dependencies:
            return True
        
        return all(dep.is_satisfied() for dep in dependencies)
    
    def update_stage_status(
        self,
        stage_id: str,
        status: SimulationStageStatus,
    ) -> List[str]:
        """
        Update a stage's status and propagate changes through the graph.
        
        Returns a list of stage IDs that may have their ready status changed.
        """
        affected_stages = []
        
        # If completed, satisfy outgoing dependencies
        if status == SimulationStageStatus.COMPLETED:
            for dep in self.get_dependencies_from(stage_id):
                if dep.state == DependencyState.PENDING:
                    dep.satisfy()
                    affected_stages.append(dep.to_stage_id)
        
        # If failed, check if any dependencies need to be marked as failed
        elif status == SimulationStageStatus.FAILED:
            for dep in self.get_dependencies_from(stage_id):
                if dep.dependency_type in [DependencyType.SEQUENTIAL, DependencyType.DATA]:
                    dep.fail()
                    affected_stages.append(dep.to_stage_id)
        
        return affected_stages
    
    def get_critical_path(self) -> List[str]:
        """Get the critical path through the graph."""
        # For this implementation, we'll just use topological sort
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Graph has cycles
            return []
    
    def get_all_paths(self, source: Optional[str] = None, target: Optional[str] = None) -> List[List[str]]:
        """Get all paths from source to target."""
        if source is None:
            sources = self.get_root_stages()
        else:
            sources = [source]
        
        if target is None:
            targets = self.get_leaf_stages()
        else:
            targets = [target]
        
        all_paths = []
        
        for s in sources:
            for t in targets:
                try:
                    paths = list(nx.all_simple_paths(self.graph, s, t))
                    all_paths.extend(paths)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue
        
        return all_paths
    
    def is_stage_blocked(self, stage_id: str, completed_stages: Set[str]) -> Optional[List[str]]:
        """
        Check if a stage is blocked and return the blocking stages.
        
        Returns None if not blocked, or a list of stage IDs blocking this stage.
        """
        if stage_id not in self.graph:
            return None
        
        # Get dependencies
        dependencies = self.get_dependencies_to(stage_id)
        
        # Check each dependency
        blocking_stages = []
        
        for dep in dependencies:
            if not dep.is_satisfied() and dep.from_stage_id not in completed_stages:
                blocking_stages.append(dep.from_stage_id)
        
        return blocking_stages if blocking_stages else None
    
    def validate(self) -> List[str]:
        """Validate the graph and return any errors."""
        errors = []
        
        # Check for cycles
        try:
            nx.find_cycle(self.graph)
            errors.append("Graph contains cycles")
        except nx.NetworkXNoCycle:
            pass
        
        # Check for disconnected components
        if not nx.is_weakly_connected(self.graph) and len(self.graph.nodes()) > 1:
            errors.append("Graph has disconnected components")
        
        # Check for consistency between graph and dependencies
        for edge in self.graph.edges():
            from_id, to_id = edge
            if (from_id, to_id) not in self.dependencies:
                errors.append(f"Edge {from_id} -> {to_id} exists in graph but not in dependencies")
        
        for (from_id, to_id) in self.dependencies:
            if not self.graph.has_edge(from_id, to_id):
                errors.append(f"Dependency {from_id} -> {to_id} exists but not in graph")
        
        return errors
    
    def serialize(self) -> Dict:
        """Serialize the graph to a dictionary."""
        nodes = []
        edges = []
        
        # Serialize nodes
        for node in self.graph.nodes():
            node_data = {
                "id": node,
                "type": self.graph.nodes[node].get("node_type", "stage"),
                "metadata": self.node_metadata.get(node, {}),
            }
            nodes.append(node_data)
        
        # Serialize edges
        for edge in self.graph.edges():
            from_id, to_id = edge
            edge_data = {
                "from": from_id,
                "to": to_id,
                "type": self.graph.edges[edge].get("type", "sequential"),
                "condition": self.graph.edges[edge].get("condition"),
                "state": self.dependencies.get((from_id, to_id), {}).state.value,
            }
            edges.append(edge_data)
        
        return {
            "simulation_id": self.simulation_id,
            "nodes": nodes,
            "edges": edges,
        }
    
    @classmethod
    def deserialize(cls, data: Dict) -> DependencyGraph:
        """Create a DependencyGraph from serialized data."""
        graph = cls(data["simulation_id"])
        
        # Add nodes
        for node_data in data["nodes"]:
            node_id = node_data["id"]
            node_type_str = node_data.get("type", "stage")
            node_type = GraphNodeType(node_type_str)
            metadata = node_data.get("metadata", {})
            
            graph.add_stage(node_id, metadata, node_type)
        
        # Add edges
        for edge_data in data["edges"]:
            from_id = edge_data["from"]
            to_id = edge_data["to"]
            
            dependency_type_str = edge_data.get("type", "sequential")
            dependency_type = DependencyType(dependency_type_str)
            
            condition = edge_data.get("condition")
            
            result = graph.add_dependency(
                from_id, to_id, dependency_type, condition
            )
            
            if result.success:
                # Set state if provided
                state_str = edge_data.get("state", "pending")
                if state_str != "pending":
                    dependency = graph.get_dependency(from_id, to_id)
                    if dependency:
                        dependency.state = DependencyState(state_str)
        
        return graph