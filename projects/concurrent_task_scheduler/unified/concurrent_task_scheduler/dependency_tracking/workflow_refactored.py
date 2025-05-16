"""Workflow management for simulations."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union

from common.core.models import Result, DependencyType
from common.dependency_tracking.workflow import (
    WorkflowTemplate as CommonWorkflowTemplate,
    WorkflowStage as CommonWorkflowStage,
    WorkflowTransition as CommonWorkflowTransition,
    WorkflowInstance as CommonWorkflowInstance,
    WorkflowManager as CommonWorkflowManager,
)

from concurrent_task_scheduler.models.simulation import (
    Simulation,
    SimulationStage,
    SimulationStageStatus,
)
from concurrent_task_scheduler.dependency_tracking.tracker_refactored import DependencyTracker

logger = logging.getLogger(__name__)


class WorkflowStage(CommonWorkflowStage):
    """A stage in a simulation workflow template."""
    
    def create_simulation_stage(self, simulation_id: str, parameters: Optional[Dict[str, Any]] = None) -> SimulationStage:
        """
        Create a simulation stage from this workflow stage.
        
        Args:
            simulation_id: ID of the simulation to create the stage for
            parameters: Optional parameters to customize the stage
            
        Returns:
            SimulationStage object
        """
        # Apply parameters to template values
        params = parameters or {}
        stage_name = self.name.format(**params) if params else self.name
        description = self.description.format(**params) if self.description and params else self.description
        
        # Create the stage
        stage = SimulationStage(
            id=f"{simulation_id}_{self.id}",
            name=stage_name,
            status=SimulationStageStatus.PENDING,
            dependencies=set(),
            estimated_duration=self.estimated_duration,
            description=description,
            resource_requirements=[req.model_copy() for req in self.resource_requirements],
        )
        
        return stage


class WorkflowTransition(CommonWorkflowTransition):
    """A transition between stages in a simulation workflow template."""
    
    def apply_to_simulation(self, simulation: Simulation, tracker: DependencyTracker) -> None:
        """
        Apply this transition to a simulation.
        
        Args:
            simulation: The simulation to apply the transition to
            tracker: The dependency tracker to register the dependency with
        """
        # Get the stage IDs in the simulation
        from_stage_id = f"{simulation.id}_{self.from_stage_id}"
        to_stage_id = f"{simulation.id}_{self.to_stage_id}"
        
        # Add dependency to the simulation
        if from_stage_id in simulation.stages and to_stage_id in simulation.stages:
            simulation.stages[to_stage_id].dependencies.add(from_stage_id)
            
            # Register with the tracker
            if tracker:
                tracker.register_dependency(
                    from_stage_id,
                    to_stage_id,
                    self.dependency_type,
                    self.condition,
                )


class WorkflowTemplate(CommonWorkflowTemplate):
    """A template for a simulation workflow."""
    
    def create_simulation(self, parameters: Optional[Dict[str, Any]] = None) -> Simulation:
        """
        Create a simulation from this template.
        
        Args:
            parameters: Optional parameters to customize the simulation
            
        Returns:
            Simulation object
        """
        # Apply parameters to template values
        params = parameters or {}
        simulation_name = self.name.format(**params) if params else self.name
        description = self.description.format(**params) if self.description and params else self.description
        
        # Create simulation with a unique ID
        import uuid
        simulation_id = f"sim-{uuid.uuid4()}"
        
        # Create stages
        stages = {}
        for stage_id, stage in self.stages.items():
            if isinstance(stage, WorkflowStage):
                simulation_stage = stage.create_simulation_stage(simulation_id, params)
                stages[simulation_stage.id] = simulation_stage
            else:
                # Create from CommonWorkflowStage
                stage_name = stage.name.format(**params) if params else stage.name
                stage_desc = stage.description.format(**params) if stage.description and params else stage.description
                
                sim_stage = SimulationStage(
                    id=f"{simulation_id}_{stage_id}",
                    name=stage_name,
                    status=SimulationStageStatus.PENDING,
                    dependencies=set(),
                    estimated_duration=stage.estimated_duration,
                    description=stage_desc,
                    resource_requirements=[req.model_copy() for req in stage.resource_requirements],
                )
                stages[sim_stage.id] = sim_stage
        
        # Calculate total duration
        total_duration = timedelta()
        for stage in stages.values():
            total_duration += stage.estimated_duration
        
        # Create the simulation
        simulation = Simulation(
            id=simulation_id,
            name=simulation_name,
            description=description,
            stages=stages,
            estimated_total_duration=total_duration,
            tags=self.tags[:] if self.tags else [],
            metadata=self.metadata.copy() if self.metadata else {},
        )
        
        # Apply transitions
        for transition in self.transitions:
            if isinstance(transition, WorkflowTransition):
                # Get the stage IDs in the simulation
                from_stage_id = f"{simulation_id}_{transition.from_stage_id}"
                to_stage_id = f"{simulation_id}_{transition.to_stage_id}"
                
                # Add dependency to the simulation
                if from_stage_id in stages and to_stage_id in stages:
                    stages[to_stage_id].dependencies.add(from_stage_id)
            else:
                # Handle CommonWorkflowTransition
                from_stage_id = f"{simulation_id}_{transition.from_stage_id}"
                to_stage_id = f"{simulation_id}_{transition.to_stage_id}"
                
                # Add dependency to the simulation
                if from_stage_id in stages and to_stage_id in stages:
                    stages[to_stage_id].dependencies.add(from_stage_id)
        
        return simulation


class WorkflowInstance(CommonWorkflowInstance):
    """An instance of a simulation workflow."""
    
    def __init__(
        self,
        template: WorkflowTemplate,
        simulation: Simulation,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a workflow instance.
        
        Args:
            template: The workflow template
            simulation: The simulation created from the template
            parameters: Parameters used to create the simulation
        """
        super().__init__(
            template_id=template.id,
            instance_id=simulation.id,
            parameters=parameters or {},
        )
        self.simulation = simulation
        self.template = template
        
    def get_simulation(self) -> Simulation:
        """
        Get the simulation associated with this workflow instance.
        
        Returns:
            The simulation
        """
        return self.simulation
    
    def update_status(self) -> None:
        """Update the status of this workflow instance."""
        # Update the simulation status
        self.simulation.update_status()
        
        # Update instance status based on simulation status
        sim_status = self.simulation.status
        if sim_status.value == "completed":
            self.status = "completed"
        elif sim_status.value == "failed":
            self.status = "failed"
        elif sim_status.value == "running":
            self.status = "running"
        elif sim_status.value == "paused":
            self.status = "paused"
        else:
            self.status = "pending"
            
        # Update progress
        self.progress = self.simulation.total_progress()


class WorkflowManager(CommonWorkflowManager):
    """Manager for simulation workflow templates and instances."""
    
    def __init__(self, tracker: Optional[DependencyTracker] = None):
        """
        Initialize a workflow manager.
        
        Args:
            tracker: Optional dependency tracker to use
        """
        super().__init__()
        self.tracker = tracker or DependencyTracker()
        self.registered_simulations: Dict[str, Simulation] = {}
        
    def create_template(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[WorkflowTemplate]:
        """
        Create a workflow template.
        
        Args:
            name: Name of the template
            description: Optional description
            metadata: Optional metadata
            
        Returns:
            Result with the created template or error
        """
        template = WorkflowTemplate(
            name=name,
            description=description,
            metadata=metadata or {},
        )
        
        self.templates[template.id] = template
        return Result.ok(template)
    
    def add_stage_to_template(
        self,
        template_id: str,
        stage_id: str,
        name: str,
        estimated_duration: timedelta,
        description: Optional[str] = None,
        resource_requirements: Optional[List[Dict[str, Any]]] = None,
    ) -> Result[WorkflowStage]:
        """
        Add a stage to a workflow template.
        
        Args:
            template_id: ID of the template
            stage_id: ID for the new stage
            name: Name of the stage
            estimated_duration: Estimated duration of the stage
            description: Optional description
            resource_requirements: Optional resource requirements
            
        Returns:
            Result with the created stage or error
        """
        if template_id not in self.templates:
            return Result.err(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Create stage
        stage = WorkflowStage(
            id=stage_id,
            name=name,
            estimated_duration=estimated_duration,
            description=description,
        )
        
        # Add resource requirements if provided
        if resource_requirements:
            from common.core.models import ResourceRequirement, ResourceType
            
            for req in resource_requirements:
                resource_type = req.get("resource_type")
                if resource_type and hasattr(ResourceType, resource_type.upper()):
                    stage.resource_requirements.append(
                        ResourceRequirement(
                            resource_type=getattr(ResourceType, resource_type.upper()),
                            amount=req.get("amount", 1.0),
                            unit=req.get("unit", "unit"),
                        )
                    )
        
        # Add to template
        template.stages[stage_id] = stage
        
        return Result.ok(stage)
    
    def add_transition_to_template(
        self,
        template_id: str,
        from_stage_id: str,
        to_stage_id: str,
        dependency_type: Union[DependencyType, str] = DependencyType.SEQUENTIAL,
        condition: Optional[str] = None,
    ) -> Result[WorkflowTransition]:
        """
        Add a transition to a workflow template.
        
        Args:
            template_id: ID of the template
            from_stage_id: ID of the source stage
            to_stage_id: ID of the target stage
            dependency_type: Type of dependency
            condition: Optional condition for the transition
            
        Returns:
            Result with the created transition or error
        """
        if template_id not in self.templates:
            return Result.err(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Check if stages exist
        if from_stage_id not in template.stages:
            return Result.err(f"Source stage {from_stage_id} not found in template {template_id}")
        
        if to_stage_id not in template.stages:
            return Result.err(f"Target stage {to_stage_id} not found in template {template_id}")
        
        # Convert dependency type if it's a string
        if isinstance(dependency_type, str):
            try:
                dependency_type = DependencyType(dependency_type)
            except ValueError:
                dependency_type = DependencyType.SEQUENTIAL
        
        # Create transition
        transition = WorkflowTransition(
            from_stage_id=from_stage_id,
            to_stage_id=to_stage_id,
            dependency_type=dependency_type,
            condition=condition,
        )
        
        # Add to template
        template.transitions.append(transition)
        
        return Result.ok(transition)
    
    def create_instance(
        self,
        template_id: str,
        simulation: Optional[Simulation] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Result[WorkflowInstance]:
        """
        Create a workflow instance from a template.
        
        Args:
            template_id: ID of the template
            simulation: Optional existing simulation to use
            parameters: Optional parameters for customization
            
        Returns:
            Result with the created instance or error
        """
        if template_id not in self.templates:
            return Result.err(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Create simulation if not provided
        if not simulation:
            if not isinstance(template, WorkflowTemplate):
                # Create a temporary WorkflowTemplate to use its create_simulation method
                temp_template = WorkflowTemplate(
                    id=template.id,
                    name=template.name,
                    description=template.description,
                    metadata=template.metadata.copy() if template.metadata else {},
                )
                
                # Copy stages and transitions
                for stage_id, stage in template.stages.items():
                    temp_template.stages[stage_id] = stage
                
                temp_template.transitions = template.transitions[:]
                
                # Create simulation
                simulation = temp_template.create_simulation(parameters)
            else:
                simulation = template.create_simulation(parameters)
        
        # Create instance
        instance = WorkflowInstance(
            template=template if isinstance(template, WorkflowTemplate) else None,
            simulation=simulation,
            parameters=parameters or {},
        )
        
        # Register with tracker
        if self.tracker:
            self.tracker.register_simulation(simulation)
        
        # Store instance
        self.instances[instance.instance_id] = instance
        self.registered_simulations[simulation.id] = simulation
        
        return Result.ok(instance)
    
    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """
        Get a workflow instance by ID.
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            The workflow instance or None if not found
        """
        return self.instances.get(instance_id)
    
    def get_simulation(self, simulation_id: str) -> Optional[Simulation]:
        """
        Get a simulation by ID.
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            The simulation or None if not found
        """
        return self.registered_simulations.get(simulation_id)
    
    def update_instance(self, instance_id: str, simulation: Simulation) -> Result[bool]:
        """
        Update a workflow instance with a new simulation state.
        
        Args:
            instance_id: ID of the instance
            simulation: Updated simulation
            
        Returns:
            Result indicating success or failure of the update
        """
        if instance_id not in self.instances:
            return Result.err(f"Instance {instance_id} not found")
        
        instance = self.instances[instance_id]
        
        # Update the simulation
        if isinstance(instance, WorkflowInstance):
            instance.simulation = simulation
            instance.update_status()
        else:
            # For non-WorkflowInstance instances, just update the progress and status
            instance.progress = simulation.total_progress() 
            status_map = {
                "completed": "completed",
                "failed": "failed",
                "running": "running",
                "paused": "paused",
            }
            instance.status = status_map.get(simulation.status.value, "pending")
        
        # Update tracker
        if self.tracker:
            self.tracker.update_from_simulation(simulation)
        
        # Update registered simulation
        self.registered_simulations[simulation.id] = simulation
        
        return Result.ok(True)