"""Dependency tracker for simulation stages."""

from typing import Dict, List, Optional, Set, Tuple, Any, Union

from common.core.models import DependencyType, Result
from common.dependency_tracking.tracker import (
    DependencyTracker as CommonDependencyTracker,
    TransitionTrigger,
    TransitionRule,
)

from concurrent_task_scheduler.dependency_tracking.graph_refactored import DependencyGraph
from concurrent_task_scheduler.models.simulation import Simulation, SimulationStage, SimulationStageStatus


class DependencyTracker(CommonDependencyTracker):
    """Dependency tracker for simulation stages."""
    
    def __init__(self):
        """Initialize the simulation dependency tracker."""
        super().__init__()
        self.registered_simulations: Dict[str, Simulation] = {}
    
    def register_simulation(self, simulation: Simulation) -> Result[bool]:
        """
        Register a simulation with the dependency tracker.
        
        Args:
            simulation: The simulation to register
            
        Returns:
            Result indicating success or failure of the registration
        """
        if simulation.id in self.registered_simulations:
            return Result.err(f"Simulation {simulation.id} is already registered")
        
        # Create a graph for this simulation
        result = self.create_graph(simulation.id)
        if not result.success:
            return result
        
        graph = result.value
        
        # If we got a regular DependencyGraph instead of a simulation-specific one, convert it
        if not isinstance(graph, DependencyGraph):
            # Create a simulation-specific graph
            sim_graph = DependencyGraph(simulation.id)
            
            # Copy all nodes and edges
            for node_id, metadata in graph.nodes.items():
                sim_graph.add_node(node_id, metadata.get("type"), metadata)
            
            for key, dependency in graph.dependencies.items():
                from_id, to_id = key
                sim_graph.add_dependency(
                    from_id, 
                    to_id, 
                    dependency.dependency_type, 
                    dependency.condition
                )
            
            # Replace the graph in the registry
            self.graphs[simulation.id] = sim_graph
            graph = sim_graph
        
        # Add stages to the graph
        graph.add_simulation_stages(simulation)
        
        # Register the simulation
        self.registered_simulations[simulation.id] = simulation
        
        return Result.ok(True)
    
    def update_stage_status(
        self,
        simulation_id: str,
        stage_id: str,
        status: Union[SimulationStageStatus, str],
    ) -> Result[List[str]]:
        """
        Update a stage's status and propagate changes.
        
        Args:
            simulation_id: ID of the simulation
            stage_id: ID of the stage
            status: New status for the stage
            
        Returns:
            Result with a list of affected stage IDs
        """
        # Call parent implementation for base functionality
        result = super().update_status(simulation_id, stage_id, status)
        
        # If successful, update the registered simulation if available
        if result.success and simulation_id in self.registered_simulations:
            simulation = self.registered_simulations[simulation_id]
            if stage_id in simulation.stages:
                # Convert status to SimulationStageStatus if it's a string
                if isinstance(status, str):
                    try:
                        status_enum = SimulationStageStatus(status)
                    except ValueError:
                        # Handle unknown status values
                        status_enum = SimulationStageStatus.PENDING
                else:
                    status_enum = status
                
                # Update status in simulation
                simulation.stages[stage_id].status = status_enum
                
                # Update simulation overall status
                simulation.update_status()
        
        return result
    
    def is_stage_ready(
        self,
        simulation_id: str,
        stage_id: str,
        completed_stages: Optional[Set[str]] = None,
    ) -> bool:
        """
        Check if a stage is ready to run based on its dependencies.
        
        Args:
            simulation_id: ID of the simulation
            stage_id: ID of the stage to check
            completed_stages: Set of completed stage IDs
            
        Returns:
            True if ready to run, False otherwise
        """
        # Use the completed_stages if provided, otherwise check the simulation
        if completed_stages is None:
            completed_stages = set()
            if simulation_id in self.registered_simulations:
                simulation = self.registered_simulations[simulation_id]
                completed_stages = {
                    stage_id for stage_id, stage in simulation.stages.items()
                    if stage.status == SimulationStageStatus.COMPLETED
                }
        
        return super().is_ready_to_run(simulation_id, stage_id, completed_stages)
    
    def get_ready_stages(
        self,
        simulation_id: str,
        completed_stages: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Get all stages that are ready to execute.
        
        Args:
            simulation_id: ID of the simulation
            completed_stages: Set of completed stage IDs
            
        Returns:
            List of stage IDs that are ready to execute
        """
        # Use the completed_stages if provided, otherwise check the simulation
        if completed_stages is None:
            completed_stages = set()
            if simulation_id in self.registered_simulations:
                simulation = self.registered_simulations[simulation_id]
                completed_stages = {
                    stage_id for stage_id, stage in simulation.stages.items()
                    if stage.status == SimulationStageStatus.COMPLETED
                }
        
        return super().get_ready_jobs(simulation_id, completed_stages)
    
    def get_execution_plan(self, simulation_id: str) -> Result[List[List[str]]]:
        """
        Generate an execution plan for a simulation.
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            Result with the execution plan or error
        """
        # Get the simulation-specific graph
        graph = self.get_graph(simulation_id)
        if not graph:
            return Result.err(f"No dependency graph found for simulation {simulation_id}")
        
        # If we have a simulation-specific graph, use its method
        if isinstance(graph, DependencyGraph):
            return graph.serialize_execution_plan()
        
        # Otherwise, fall back to parent implementation
        return super().get_execution_plan(simulation_id)
    
    def update_from_simulation(self, simulation: Simulation) -> Result[bool]:
        """
        Update the dependency tracker with the current state of a simulation.
        
        Args:
            simulation: The simulation to update from
            
        Returns:
            Result indicating success or failure of the update
        """
        if simulation.id not in self.graphs:
            # If the simulation is not registered, register it first
            return self.register_simulation(simulation)
        
        # Get the graph
        graph = self.get_graph(simulation.id)
        if not graph:
            return Result.err(f"No dependency graph found for simulation {simulation.id}")
        
        # Update registered simulation
        self.registered_simulations[simulation.id] = simulation
        
        # If we have a simulation-specific graph, use its method
        if isinstance(graph, DependencyGraph):
            # Update stage statuses in the graph
            affected_stages = graph.update_stage_statuses(simulation)
            return Result.ok(True)
        
        # Otherwise, update manually
        affected_stages = []
        for stage_id, stage in simulation.stages.items():
            # If the stage is not in the graph, add it
            if stage_id not in graph.nodes:
                if isinstance(graph, DependencyGraph):
                    graph.add_stage_object(stage)
                else:
                    graph.add_node(stage_id, "stage", {
                        "name": stage.name,
                        "status": stage.status,
                    })
                
                # Add dependencies from stage object
                for dep_id in stage.dependencies:
                    if dep_id in graph.nodes:
                        graph.add_dependency(
                            dep_id, 
                            stage_id, 
                            DependencyType.SEQUENTIAL
                        )
            else:
                # Update status in the graph
                if stage.status == SimulationStageStatus.COMPLETED:
                    affected_stages.extend(graph.update_node_status(stage_id, "completed"))
        
        return Result.ok(True)
    
    def validate_simulation(self, simulation: Union[str, Simulation]) -> List[str]:
        """
        Validate a simulation's dependency structure.
        
        Args:
            simulation: The simulation to validate or its ID
            
        Returns:
            List of error messages, empty if valid
        """
        if isinstance(simulation, Simulation):
            simulation_id = simulation.id
        else:
            simulation_id = simulation
        
        return super().validate(simulation_id)