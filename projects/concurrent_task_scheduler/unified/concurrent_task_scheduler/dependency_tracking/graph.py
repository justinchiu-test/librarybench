"""Dependency graph implementation for simulation dependency tracking."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set, Tuple, Union

# Import from common library
from common.dependency_tracking.graph import (
    DependencyGraph as CommonDependencyGraph,
    GraphNodeType,
)
from common.core.models import (
    Dependency,
    DependencyState,
    DependencyType,
    Result,
)

from concurrent_task_scheduler.models import (
    Simulation,
    SimulationStage,
    SimulationStageStatus,
)

logger = logging.getLogger(__name__)


# For backwards compatibility, expose the classes from common library
SimulationDependency = Dependency


class DependencyGraph(CommonDependencyGraph):
    """
    A graph representing dependencies between simulation stages.
    
    This extends the common DependencyGraph implementation with
    simulation-specific functionality.
    """

    def __init__(self, simulation_id: str = "default-simulation"):
        """Initialize the dependency graph with a simulation ID."""
        super().__init__(simulation_id)
    
    def get_simulation_dependencies(self, simulation_id: str) -> List[str]:
        """Get all dependencies for a simulation."""
        # In this simplified implementation, we just return the predecessors
        # of the simulation node in the graph
        if simulation_id in self.nodes:
            return list(self.graph.predecessors(simulation_id)) if hasattr(self.graph, 'predecessors') else []
        return []
    
    def add_stage(
        self,
        stage_id: str,
        metadata: Optional[Dict[str, str]] = None,
        node_type: GraphNodeType = GraphNodeType.STAGE,
    ) -> None:
        """Add a stage to the dependency graph."""
        self.add_node(stage_id, node_type, metadata)
    
    def get_dependencies_to(self, stage_id: str) -> List[Dependency]:
        """Get all dependencies pointing to a stage."""
        return super().get_dependencies_to(stage_id)
    
    def get_dependencies_from(self, stage_id: str) -> List[Dependency]:
        """Get all dependencies from a stage."""
        return super().get_dependencies_from(stage_id)
    
    def get_root_stages(self) -> List[str]:
        """Get all stages that have no incoming dependencies."""
        return super().get_root_nodes()
    
    def get_leaf_stages(self) -> List[str]:
        """Get all stages that have no outgoing dependencies."""
        return super().get_leaf_nodes()
    
    def get_ready_stages(self, completed_stages: Set[str]) -> List[str]:
        """Get all stages that are ready to execute."""
        return list(super().get_ready_nodes(completed_stages))
    
    def are_all_dependencies_satisfied(self, stage_id: str) -> bool:
        """Check if all dependencies to a stage are satisfied."""
        return super().are_all_dependencies_satisfied(stage_id)
    
    def update_stage_status(
        self,
        stage_id: str,
        status: SimulationStageStatus,
    ) -> List[str]:
        """
        Update a stage's status and propagate changes through the graph.
        
        Returns a list of stage IDs that may have their ready status changed.
        """
        # Map SimulationStageStatus to our internal JobStatus
        status_str = status.value
        
        # Update through the common implementation
        affected_stages = super().update_node_status(stage_id, status_str)
        
        return affected_stages
    
    def get_critical_path(self) -> List[str]:
        """Get the critical path through the graph."""
        return super().get_critical_path()
    
    def get_all_paths(self, source: Optional[str] = None, target: Optional[str] = None) -> List[List[str]]:
        """Get all paths from source to target."""
        import networkx as nx
        
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
        return super().is_node_blocked(stage_id, completed_stages)
    
    def validate(self) -> List[str]:
        """Validate the graph and return any errors."""
        return super().validate()
    
    def serialize(self) -> Dict:
        """Serialize the graph to a dictionary."""
        return super().serialize()
    
    @classmethod
    def deserialize(cls, data: Dict) -> DependencyGraph:
        """Create a DependencyGraph from serialized data."""
        graph = super().deserialize(data)
        
        # Convert to our subclass type
        if not isinstance(graph, cls):
            result = cls(graph.owner_id)
            result.nodes = graph.nodes
            result.dependencies = graph.dependencies
            result.graph = graph.graph
            if hasattr(graph, 'adjacency_list'):
                result.adjacency_list = graph.adjacency_list
                result.reverse_adjacency_list = graph.reverse_adjacency_list
            
            return result
        
        return graph