"""
Strategic objective management module for ProductInsight.

This module provides functionality for managing strategic objectives and goals,
including hierarchical structures and progress tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union, cast
from uuid import UUID

from pydantic import BaseModel, validator

from product_insight.models import (
    MetricTypeEnum,
    PriorityEnum,
    StatusEnum,
    StrategicObjective,
    Tag,
)
from product_insight.storage import FileStorage, StorageInterface


class ObjectiveProgress(BaseModel):
    """Progress information for a strategic objective."""
    
    objective_id: UUID
    name: str
    metric_type: Optional[MetricTypeEnum] = None
    metric_target: Optional[float] = None
    metric_current: Optional[float] = None
    progress_percentage: Optional[float] = None
    status: StatusEnum
    priority: PriorityEnum
    child_progress: List["ObjectiveProgress"] = []
    
    @validator("progress_percentage", always=True)
    def calculate_progress(cls, v: Optional[float], values: Dict) -> Optional[float]:
        """Calculate progress percentage if not provided."""
        if v is not None:
            return v
        
        if (
            values.get("metric_target") is not None and 
            values.get("metric_current") is not None and
            values.get("metric_target") > 0
        ):
            return min(100.0, (values["metric_current"] / values["metric_target"]) * 100.0)
        
        return None


class ObjectiveTree(BaseModel):
    """Tree representation of a strategic objective hierarchy."""
    
    root: StrategicObjective
    children: List["ObjectiveTree"] = []


class ObjectiveManager:
    """Manages strategic objectives and their hierarchical structure."""
    
    def __init__(
        self,
        storage_dir: str,
        objective_storage: Optional[StorageInterface[StrategicObjective]] = None,
    ):
        """Initialize the objective manager.
        
        Args:
            storage_dir: Base directory for storing objective data
            objective_storage: Optional custom storage for objectives
        """
        self.objective_storage = objective_storage or FileStorage(
            entity_type=StrategicObjective,
            storage_dir=f"{storage_dir}/objectives",
            format="json"
        )
    
    def add_objective(self, objective: StrategicObjective) -> StrategicObjective:
        """Add a new strategic objective.
        
        Args:
            objective: Strategic objective to add
            
        Returns:
            Added strategic objective
        """
        # If this is a child objective, update the parent
        if objective.parent_id:
            try:
                parent = self.objective_storage.get(objective.parent_id)
                if objective.id not in parent.child_ids:
                    parent.child_ids.append(objective.id)
                    self.objective_storage.save(parent)
            except Exception as e:
                print(f"Error updating parent objective: {e}")
        
        return self.objective_storage.save(objective)
    
    def update_objective(self, objective: StrategicObjective) -> StrategicObjective:
        """Update an existing strategic objective.
        
        Args:
            objective: Strategic objective to update
            
        Returns:
            Updated strategic objective
        """
        existing = self.objective_storage.get(objective.id)
        
        # Check if parent has changed
        if existing.parent_id != objective.parent_id:
            # Remove from old parent
            if existing.parent_id:
                try:
                    old_parent = self.objective_storage.get(existing.parent_id)
                    if objective.id in old_parent.child_ids:
                        old_parent.child_ids.remove(objective.id)
                        self.objective_storage.save(old_parent)
                except Exception as e:
                    print(f"Error updating old parent objective: {e}")
            
            # Add to new parent
            if objective.parent_id:
                try:
                    new_parent = self.objective_storage.get(objective.parent_id)
                    if objective.id not in new_parent.child_ids:
                        new_parent.child_ids.append(objective.id)
                        self.objective_storage.save(new_parent)
                except Exception as e:
                    print(f"Error updating new parent objective: {e}")
        
        return self.objective_storage.save(objective)
    
    def delete_objective(self, objective_id: UUID, cascade: bool = False) -> bool:
        """Delete a strategic objective.
        
        Args:
            objective_id: ID of the objective to delete
            cascade: Whether to delete all child objectives
            
        Returns:
            True if the objective was deleted, False otherwise
        """
        objective = self.objective_storage.get(objective_id)
        
        # Delete from parent's child list
        if objective.parent_id:
            try:
                parent = self.objective_storage.get(objective.parent_id)
                if objective_id in parent.child_ids:
                    parent.child_ids.remove(objective_id)
                    self.objective_storage.save(parent)
            except Exception as e:
                print(f"Error updating parent objective: {e}")
        
        # Handle children
        if objective.child_ids:
            if cascade:
                # Delete all children
                for child_id in objective.child_ids:
                    self.delete_objective(child_id, cascade=True)
            else:
                # Move children to the parent
                for child_id in objective.child_ids:
                    try:
                        child = self.objective_storage.get(child_id)
                        child.parent_id = objective.parent_id
                        self.objective_storage.save(child)
                        
                        # Update the parent's child list
                        if objective.parent_id:
                            parent = self.objective_storage.get(objective.parent_id)
                            if child_id not in parent.child_ids:
                                parent.child_ids.append(child_id)
                                self.objective_storage.save(parent)
                    except Exception as e:
                        print(f"Error updating child objective: {e}")
        
        # Delete the objective
        return self.objective_storage.delete(objective_id)
    
    def get_objective_tree(self, root_id: UUID) -> ObjectiveTree:
        """Get a hierarchical tree representation of an objective and its children.
        
        Args:
            root_id: ID of the root objective
            
        Returns:
            ObjectiveTree with the root objective and its children
        """
        root = self.objective_storage.get(root_id)
        children = []
        
        for child_id in root.child_ids:
            try:
                child_tree = self.get_objective_tree(child_id)
                children.append(child_tree)
            except Exception as e:
                print(f"Error getting child objective tree: {e}")
        
        return ObjectiveTree(root=root, children=children)
    
    def get_root_objectives(self) -> List[StrategicObjective]:
        """Get all root objectives (objectives with no parent).
        
        Returns:
            List of root objectives
        """
        all_objectives = self.objective_storage.list()
        return [obj for obj in all_objectives if obj.parent_id is None]
    
    def calculate_objective_progress(self, objective_id: UUID) -> ObjectiveProgress:
        """Calculate progress for an objective and its children.
        
        Args:
            objective_id: ID of the objective
            
        Returns:
            ObjectiveProgress with progress information
        """
        objective = self.objective_storage.get(objective_id)
        
        # Calculate progress for children
        child_progress = []
        for child_id in objective.child_ids:
            try:
                child_prog = self.calculate_objective_progress(child_id)
                child_progress.append(child_prog)
            except Exception as e:
                print(f"Error calculating child objective progress: {e}")
        
        # Calculate progress percentage
        progress_percentage = None
        if objective.metric_target is not None and objective.metric_current is not None:
            if objective.metric_target > 0:
                progress_percentage = min(
                    100.0, 
                    (objective.metric_current / objective.metric_target) * 100.0
                )
        elif child_progress:
            # If no direct metrics, average children's progress
            valid_children = [
                cp for cp in child_progress if cp.progress_percentage is not None
            ]
            if valid_children:
                progress_percentage = sum(
                    cp.progress_percentage for cp in valid_children
                ) / len(valid_children)
        
        return ObjectiveProgress(
            objective_id=objective.id,
            name=objective.name,
            metric_type=objective.metric_type,
            metric_target=objective.metric_target,
            metric_current=objective.metric_current,
            progress_percentage=progress_percentage,
            status=objective.status,
            priority=objective.priority,
            child_progress=child_progress
        )
    
    def calculate_alignment_score(
        self, feature_objectives: List[UUID], all_objectives: Optional[List[StrategicObjective]] = None
    ) -> float:
        """Calculate a strategic alignment score for a set of feature objectives.
        
        Args:
            feature_objectives: List of objective IDs associated with a feature
            all_objectives: Optional list of all objectives for caching
            
        Returns:
            Alignment score between 0 and 1
        """
        if not feature_objectives:
            return 0.0
        
        if all_objectives is None:
            all_objectives = self.objective_storage.list()
        
        # Create an ID to objective mapping for quick lookups
        objective_map = {obj.id: obj for obj in all_objectives}
        
        # Calculate the weighted score based on objective priority
        priority_weights = {
            PriorityEnum.CRITICAL: 1.0,
            PriorityEnum.HIGH: 0.8,
            PriorityEnum.MEDIUM: 0.5,
            PriorityEnum.LOW: 0.3,
            PriorityEnum.NONE: 0.1,
        }
        
        total_weight = 0.0
        total_score = 0.0
        
        for obj_id in feature_objectives:
            if obj_id in objective_map:
                obj = objective_map[obj_id]
                weight = priority_weights.get(obj.priority, 0.5)
                total_weight += weight
                total_score += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def find_objectives_by_tags(self, tags: List[str]) -> List[StrategicObjective]:
        """Find objectives matching a set of tags.
        
        Args:
            tags: List of tag names to match
            
        Returns:
            List of matching objectives
        """
        all_objectives = self.objective_storage.list()
        tag_set = set(t.lower() for t in tags)
        
        matching_objectives = []
        for obj in all_objectives:
            obj_tags = set(t.name.lower() for t in obj.tags)
            if obj_tags.intersection(tag_set):
                matching_objectives.append(obj)
        
        return matching_objectives
    
    def get_objectives_by_priority(self, priority: PriorityEnum) -> List[StrategicObjective]:
        """Get objectives with a specific priority.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of matching objectives
        """
        all_objectives = self.objective_storage.list()
        return [obj for obj in all_objectives if obj.priority == priority]
    
    def get_objectives_by_status(self, status: StatusEnum) -> List[StrategicObjective]:
        """Get objectives with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of matching objectives
        """
        all_objectives = self.objective_storage.list()
        return [obj for obj in all_objectives if obj.status == status]
    
    def get_objectives_by_timeframe(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[StrategicObjective]:
        """Get objectives within a specific timeframe.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of matching objectives
        """
        all_objectives = self.objective_storage.list()
        filtered = []
        
        for obj in all_objectives:
            if start_date and obj.timeframe_end and obj.timeframe_end < start_date:
                continue
            if end_date and obj.timeframe_start and obj.timeframe_start > end_date:
                continue
            filtered.append(obj)
        
        return filtered