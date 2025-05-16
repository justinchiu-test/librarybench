"""Graph-based dependency tracking system for simulations."""

from typing import Dict, List, Optional, Set, Tuple, Union

from common.core.models import Result
from common.dependency_tracking.graph import DependencyGraph as CommonDependencyGraph, GraphNodeType

from concurrent_task_scheduler.models.simulation import Simulation, SimulationStage


class DependencyGraph(CommonDependencyGraph):
    """
    Graph-based representation of dependencies between simulation stages.
    
    Extends the common dependency graph with simulation-specific functionality.
    """
    
    def __init__(self, simulation_id: str = ""):
        """
        Initialize a simulation dependency graph.
        
        Args:
            simulation_id: ID of the simulation this graph belongs to
        """
        super().__init__(owner_id=simulation_id)
        self.simulation_id = simulation_id  # Alias for compatibility
        
    def add_stage(self, stage_id: str, metadata: Optional[Dict] = None) -> None:
        """
        Add a simulation stage to the graph.
        
        Args:
            stage_id: ID of the stage
            metadata: Optional metadata for the stage
        """
        super().add_node(stage_id, GraphNodeType.STAGE, metadata)
    
    def add_stage_object(self, stage: SimulationStage) -> None:
        """
        Add a simulation stage object to the graph.
        
        Args:
            stage: The simulation stage to add
        """
        metadata = {
            "name": stage.name,
            "status": stage.status,
            "dependencies": list(stage.dependencies),
            "stage": stage,
        }
        self.add_stage(stage.id, metadata)
        
        # Add dependencies from stage object
        for dep_id in stage.dependencies:
            if dep_id in self.nodes:
                self.add_dependency(dep_id, stage.id)
    
    def add_simulation_stages(self, simulation: Simulation) -> None:
        """
        Add all stages from a simulation to the graph.
        
        Args:
            simulation: The simulation containing stages to add
        """
        # Add all stages first
        for stage_id, stage in simulation.stages.items():
            self.add_stage_object(stage)
        
        # Then add dependencies
        for stage_id, stage in simulation.stages.items():
            for dep_id in stage.dependencies:
                if dep_id in simulation.stages:
                    self.add_dependency(dep_id, stage_id)
    
    def update_stage_statuses(self, simulation: Simulation) -> None:
        """
        Update stage statuses in the graph from a simulation.
        
        Args:
            simulation: The simulation with updated stage statuses
        """
        affected_stages = []
        
        for stage_id, stage in simulation.stages.items():
            if stage_id in self.nodes:
                # Update status in metadata
                self.nodes[stage_id]["status"] = stage.status
                
                # Propagate completed status
                if stage.status == "completed":
                    affected_stages.extend(self.update_node_status(stage_id, "completed"))
        
        return affected_stages
    
    def get_execution_order(self) -> List[List[str]]:
        """
        Generate an execution order for the stages in this graph.
        
        Returns:
            List of lists, where each inner list represents stages that can
            be executed in parallel.
        """
        result = self.serialize_execution_plan()
        if result.success and result.value:
            return result.value
        return []
    
    def serialize_execution_plan(self) -> Result[List[List[str]]]:
        """
        Serialize the execution plan for this graph.
        
        Returns:
            Result with a list of lists, where each inner list represents stages
            that can be executed in parallel.
        """
        import networkx as nx
        
        try:
            # Group nodes by their depth in the graph
            node_depths = {}
            
            # Initialize depths for roots
            roots = self.get_root_nodes()
            for root in roots:
                node_depths[root] = 0
            
            # Get nodes in topological order
            try:
                sorted_nodes = list(nx.topological_sort(self.graph))
            except:
                # Fallback if topological_sort method is not available
                sorted_nodes = list(self.nodes.keys())
            
            # Compute depths for all nodes
            for node in sorted_nodes:
                if node in node_depths:
                    continue
                
                # Find max depth of dependencies
                max_depth = -1
                for dep in self.get_dependencies_to(node):
                    if dep.from_id in node_depths:
                        max_depth = max(max_depth, node_depths[dep.from_id])
                
                node_depths[node] = max_depth + 1
            
            # Group nodes by depth
            depth_groups = {}
            for node, depth in node_depths.items():
                if depth not in depth_groups:
                    depth_groups[depth] = []
                depth_groups[depth].append(node)
            
            # Convert to execution plan
            execution_plan = []
            for depth in sorted(depth_groups.keys()):
                execution_plan.append(depth_groups[depth])
            
            return Result.ok(execution_plan)
        except Exception as e:
            return Result.err(f"Error generating execution plan: {str(e)}")