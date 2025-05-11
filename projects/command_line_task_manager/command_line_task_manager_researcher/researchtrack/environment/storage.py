from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Union
from uuid import UUID

from .models import (
    EnvironmentSnapshot, 
    PackageInfo, 
    ComputeResource, 
    TaskEnvironmentLink
)


class EnvironmentStorageInterface(ABC):
    """Abstract interface for environment snapshot storage implementations."""
    
    @abstractmethod
    def create_snapshot(self, snapshot: EnvironmentSnapshot) -> UUID:
        """
        Create a new environment snapshot.
        
        Args:
            snapshot: The snapshot to create
            
        Returns:
            UUID: The ID of the created snapshot
        """
        pass
    
    @abstractmethod
    def get_snapshot(self, snapshot_id: UUID) -> Optional[EnvironmentSnapshot]:
        """
        Retrieve a snapshot by ID.
        
        Args:
            snapshot_id: The ID of the snapshot to retrieve
            
        Returns:
            Optional[EnvironmentSnapshot]: The snapshot if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_snapshot(self, snapshot: EnvironmentSnapshot) -> bool:
        """
        Update an existing snapshot.
        
        Args:
            snapshot: The snapshot with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_snapshot(self, snapshot_id: UUID) -> bool:
        """
        Delete a snapshot by ID.
        
        Args:
            snapshot_id: The ID of the snapshot to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_snapshots(
        self, environment_type: Optional[str] = None, tags: Optional[Set[str]] = None
    ) -> List[EnvironmentSnapshot]:
        """
        List snapshots with optional filtering.
        
        Args:
            environment_type: Filter by environment type
            tags: Filter by tags (snapshots must have all specified tags)
            
        Returns:
            List[EnvironmentSnapshot]: List of snapshots matching the criteria
        """
        pass
    
    @abstractmethod
    def create_task_environment_link(self, link: TaskEnvironmentLink) -> UUID:
        """
        Create a link between a task and an environment snapshot.
        
        Args:
            link: The link to create
            
        Returns:
            UUID: The ID of the created link
        """
        pass
    
    @abstractmethod
    def get_task_environment_link(self, link_id: UUID) -> Optional[TaskEnvironmentLink]:
        """
        Retrieve a task-environment link by ID.
        
        Args:
            link_id: The ID of the link to retrieve
            
        Returns:
            Optional[TaskEnvironmentLink]: The link if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_task_environment_link(self, link: TaskEnvironmentLink) -> bool:
        """
        Update an existing task-environment link.
        
        Args:
            link: The link with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_task_environment_link(self, link_id: UUID) -> bool:
        """
        Delete a task-environment link by ID.
        
        Args:
            link_id: The ID of the link to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_snapshots_for_task(self, task_id: UUID) -> List[EnvironmentSnapshot]:
        """
        Get all environment snapshots associated with a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[EnvironmentSnapshot]: List of associated snapshots
        """
        pass
    
    @abstractmethod
    def get_tasks_for_snapshot(self, snapshot_id: UUID) -> List[UUID]:
        """
        Get all task IDs associated with an environment snapshot.
        
        Args:
            snapshot_id: The ID of the snapshot
            
        Returns:
            List[UUID]: List of associated task IDs
        """
        pass


class InMemoryEnvironmentStorage(EnvironmentStorageInterface):
    """In-memory implementation of environment snapshot storage."""
    
    def __init__(self):
        self._snapshots: Dict[UUID, EnvironmentSnapshot] = {}
        self._task_environment_links: Dict[UUID, TaskEnvironmentLink] = {}
    
    def create_snapshot(self, snapshot: EnvironmentSnapshot) -> UUID:
        self._snapshots[snapshot.id] = snapshot
        return snapshot.id
    
    def get_snapshot(self, snapshot_id: UUID) -> Optional[EnvironmentSnapshot]:
        return self._snapshots.get(snapshot_id)
    
    def update_snapshot(self, snapshot: EnvironmentSnapshot) -> bool:
        if snapshot.id not in self._snapshots:
            return False
        self._snapshots[snapshot.id] = snapshot
        return True
    
    def delete_snapshot(self, snapshot_id: UUID) -> bool:
        if snapshot_id not in self._snapshots:
            return False
        
        # Delete the snapshot
        del self._snapshots[snapshot_id]
        
        # Delete any links that reference this snapshot
        links_to_delete = [
            link_id for link_id, link in self._task_environment_links.items()
            if link.environment_id == snapshot_id
        ]
        for link_id in links_to_delete:
            self.delete_task_environment_link(link_id)
        
        return True
    
    def list_snapshots(
        self, environment_type: Optional[str] = None, tags: Optional[Set[str]] = None
    ) -> List[EnvironmentSnapshot]:
        snapshots = list(self._snapshots.values())
        
        if environment_type:
            snapshots = [
                snap for snap in snapshots if snap.type == environment_type
            ]
        
        if tags:
            snapshots = [
                snap for snap in snapshots
                if all(tag in snap.tags for tag in tags)
            ]
        
        return snapshots
    
    def create_task_environment_link(self, link: TaskEnvironmentLink) -> UUID:
        self._task_environment_links[link.id] = link
        return link.id
    
    def get_task_environment_link(self, link_id: UUID) -> Optional[TaskEnvironmentLink]:
        return self._task_environment_links.get(link_id)
    
    def update_task_environment_link(self, link: TaskEnvironmentLink) -> bool:
        if link.id not in self._task_environment_links:
            return False
        self._task_environment_links[link.id] = link
        return True
    
    def delete_task_environment_link(self, link_id: UUID) -> bool:
        if link_id not in self._task_environment_links:
            return False
        del self._task_environment_links[link_id]
        return True
    
    def get_snapshots_for_task(self, task_id: UUID) -> List[EnvironmentSnapshot]:
        # Get all links for this task
        links = [
            link for link in self._task_environment_links.values()
            if link.task_id == task_id
        ]
        
        # Get all associated snapshots
        snapshots = []
        for link in links:
            snapshot = self.get_snapshot(link.environment_id)
            if snapshot:
                snapshots.append(snapshot)
        
        return snapshots
    
    def get_tasks_for_snapshot(self, snapshot_id: UUID) -> List[UUID]:
        # Get all links for this snapshot
        links = [
            link for link in self._task_environment_links.values()
            if link.environment_id == snapshot_id
        ]
        
        # Return task IDs
        return [link.task_id for link in links]