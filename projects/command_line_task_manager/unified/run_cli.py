#!/usr/bin/env python3
"""
Simple wrapper script to run the command-line task manager.
"""

import argparse
import json
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Task Status and Priority Enums
class TaskStatusEnum(str, Enum):
    """Common status values for tasks across all implementations."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriorityEnum(str, Enum):
    """Common priority levels for tasks across all implementations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types of tasks supported by the unified task manager."""
    GENERIC = "generic"
    RESEARCH = "research"
    SECURITY = "security"


# Base Models
class BaseEntity(BaseModel):
    """Base model for all entities with common fields and methods."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()


class BaseTask(BaseEntity):
    """Base model for tasks with common fields and methods."""
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Organizational attributes
    tags: Set[str] = Field(default_factory=set)
    notes: List[str] = Field(default_factory=list)
    
    # Task relationships
    parent_id: Optional[UUID] = None
    subtask_ids: Set[UUID] = Field(default_factory=set)
    
    # Custom metadata for extensibility
    custom_metadata: Dict[str, Union[str, int, float, bool, list, dict]] = Field(
        default_factory=dict
    )
    
    def update(self, **kwargs) -> None:
        super().update(**kwargs)
        
        # Update completion timestamp if status changed to completed
        if self.status == "completed" and not self.completed_at:
            self.completed_at = datetime.now()
    
    def add_note(self, note: str) -> None:
        self.notes.append(note)
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> bool:
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_subtask(self, subtask_id: UUID) -> None:
        self.subtask_ids.add(subtask_id)
        self.updated_at = datetime.now()
    
    def remove_subtask(self, subtask_id: UUID) -> bool:
        if subtask_id in self.subtask_ids:
            self.subtask_ids.remove(subtask_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_custom_metadata(self, key: str, value: Union[str, int, float, bool, list, dict]) -> None:
        self.custom_metadata[key] = value
        self.updated_at = datetime.now()
    
    def remove_custom_metadata(self, key: str) -> bool:
        if key in self.custom_metadata:
            del self.custom_metadata[key]
            self.updated_at = datetime.now()
            return True
        return False


class UnifiedTask(BaseTask):
    """Unified task model that combines fields from research and security tasks."""
    # Research-specific fields
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    
    # Security-specific fields
    severity: Optional[str] = None
    affected_systems: List[str] = Field(default_factory=list)
    discovered_by: Optional[str] = None


# Storage
class InMemoryStorage:
    """In-memory implementation of entity storage."""
    
    def __init__(self):
        self._entities = {}
    
    def create(self, entity):
        self._entities[entity.id] = entity
        return entity.id
    
    def get(self, entity_id):
        return self._entities.get(entity_id)
    
    def update(self, entity):
        if entity.id not in self._entities:
            return False
        self._entities[entity.id] = entity
        return True
    
    def delete(self, entity_id):
        if entity_id not in self._entities:
            return False
        del self._entities[entity_id]
        return True
    
    def list(self, filters=None):
        entities = list(self._entities.values())
        
        if not filters:
            return entities
        
        # Apply filters
        filtered_entities = []
        for entity in entities:
            if self._matches_filters(entity, filters):
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _matches_filters(self, entity, filters):
        for field, value in filters.items():
            if not hasattr(entity, field):
                return False
                
            field_value = getattr(entity, field)
            
            # Handle list fields like tags
            if isinstance(field_value, list) and not isinstance(value, list):
                if value not in field_value:
                    return False
            # Handle set fields
            elif isinstance(field_value, set) and not isinstance(value, set):
                if value not in field_value:
                    return False
            # Simple equality
            elif field_value != value:
                return False
                
        return True
    
    def get_tasks_by_tag(self, tag):
        return [
            task for task in self._entities.values()
            if hasattr(task, 'tags') and tag in task.tags
        ]
    
    def get_tasks_by_status(self, status):
        return [
            task for task in self._entities.values()
            if hasattr(task, 'status') and task.status == status
        ]
    
    def get_subtasks(self, parent_id):
        return [
            task for task in self._entities.values()
            if hasattr(task, 'parent_id') and task.parent_id == parent_id
        ]


# Task Manager
class UnifiedTaskManager:
    """Unified task manager with functionality for both personas."""
    
    def __init__(self, storage=None):
        self._storage = storage or InMemoryStorage()
    
    def create_task(
        self,
        title: str,
        description: str,
        task_type: str = TaskType.GENERIC,
        status: str = TaskStatusEnum.PLANNED,
        priority: str = TaskPriorityEnum.MEDIUM,
        due_date: Optional[datetime] = None,
        parent_id: Optional[UUID] = None,
        tags: Optional[Set[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        severity: Optional[str] = None,
        affected_systems: Optional[List[str]] = None,
        discovered_by: Optional[str] = None,
    ) -> UUID:
        # Validate parent task if provided
        if parent_id:
            parent_task = self._storage.get(parent_id)
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_id} does not exist")
        
        # Create task
        task = UnifiedTask(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            parent_id=parent_id,
            tags=tags or set(),
            custom_metadata=custom_metadata or {},
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            severity=severity,
            affected_systems=affected_systems or [],
            discovered_by=discovered_by,
        )
        
        # Add task type to metadata
        task.update_custom_metadata("task_type", task_type)
        
        # Save task
        task_id = self._storage.create(task)
        
        # Update parent task if needed
        if parent_id:
            parent_task = self._storage.get(parent_id)
            if parent_task:
                parent_task.add_subtask(task_id)
                self._storage.update(parent_task)
        
        return task_id
    
    def get_task(self, task_id: UUID) -> Optional[UnifiedTask]:
        task = self._storage.get(task_id)
        return task
    
    def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        severity: Optional[str] = None,
        affected_systems: Optional[List[str]] = None,
        discovered_by: Optional[str] = None,
    ) -> bool:
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if due_date is not None:
            update_data["due_date"] = due_date
        if estimated_hours is not None:
            update_data["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            update_data["actual_hours"] = actual_hours
        if severity is not None:
            update_data["severity"] = severity
        if affected_systems is not None:
            update_data["affected_systems"] = affected_systems
        if discovered_by is not None:
            update_data["discovered_by"] = discovered_by
        
        task.update(**update_data)
        return self._storage.update(task)
    
    def delete_task(self, task_id: UUID) -> bool:
        return self._storage.delete(task_id)
    
    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[UnifiedTask]:
        return self._storage.list(filters)
    
    def get_tasks_by_type(self, task_type: str) -> List[UnifiedTask]:
        tasks = self._storage.list()
        return [
            task for task in tasks
            if task.custom_metadata.get("task_type") == task_type
        ]
    
    def get_tasks_by_status(self, status: str) -> List[UnifiedTask]:
        return self._storage.get_tasks_by_status(status)
    
    def get_tasks_by_tag(self, tag: str) -> List[UnifiedTask]:
        return self._storage.get_tasks_by_tag(tag)
    
    def add_task_note(self, task_id: UUID, note: str) -> bool:
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_note(note)
        return self._storage.update(task)
    
    def add_task_tag(self, task_id: UUID, tag: str) -> bool:
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_tag(tag)
        return self._storage.update(task)
    
    def remove_task_tag(self, task_id: UUID, tag: str) -> bool:
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        result = task.remove_tag(tag)
        if result:
            self._storage.update(task)
        return result


# Command Handlers
def format_task_for_display(task: Dict[str, Any], json_output: bool = False) -> str:
    """Format a task for display."""
    if json_output:
        # Convert UUID and datetime objects to strings for JSON serialization
        task_copy = task.copy()
        if "id" in task_copy and isinstance(task_copy["id"], UUID):
            task_copy["id"] = str(task_copy["id"])
        if "created_at" in task_copy and isinstance(task_copy["created_at"], datetime):
            task_copy["created_at"] = task_copy["created_at"].isoformat()
        if "updated_at" in task_copy and isinstance(task_copy["updated_at"], datetime):
            task_copy["updated_at"] = task_copy["updated_at"].isoformat()
        if "due_date" in task_copy and task_copy["due_date"] and isinstance(task_copy["due_date"], datetime):
            task_copy["due_date"] = task_copy["due_date"].isoformat()
        if "completed_at" in task_copy and task_copy["completed_at"] and isinstance(task_copy["completed_at"], datetime):
            task_copy["completed_at"] = task_copy["completed_at"].isoformat()
        if "parent_id" in task_copy and task_copy["parent_id"] and isinstance(task_copy["parent_id"], UUID):
            task_copy["parent_id"] = str(task_copy["parent_id"])
        if "subtask_ids" in task_copy and task_copy["subtask_ids"]:
            task_copy["subtask_ids"] = [str(id) for id in task_copy["subtask_ids"]]
        
        return json.dumps(task_copy, indent=2)
    
    # Text format
    output = []
    output.append(f"ID: {task.get('id')}")
    output.append(f"Title: {task.get('title')}")
    output.append(f"Description: {task.get('description')}")
    output.append(f"Status: {task.get('status')}")
    output.append(f"Priority: {task.get('priority')}")
    
    if task.get("due_date"):
        output.append(f"Due Date: {task.get('due_date').strftime('%Y-%m-%d')}")
    
    if task.get("tags"):
        output.append(f"Tags: {', '.join(task.get('tags'))}")
    
    # Research-specific fields
    if task.get("estimated_hours") is not None:
        output.append(f"Estimated Hours: {task.get('estimated_hours')}")
    if task.get("actual_hours") is not None:
        output.append(f"Actual Hours: {task.get('actual_hours')}")
    
    # Security-specific fields
    if task.get("severity"):
        output.append(f"Severity: {task.get('severity')}")
    if task.get("affected_systems"):
        output.append(f"Affected Systems: {', '.join(task.get('affected_systems'))}")
    if task.get("discovered_by"):
        output.append(f"Discovered By: {task.get('discovered_by')}")
    
    if task.get("notes"):
        output.append("\nNotes:")
        for i, note in enumerate(task.get("notes"), 1):
            output.append(f"  {i}. {note}")
    
    return "\n".join(output)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="tasks",
        description="Unified command-line task manager for researchers and security analysts",
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create task command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("--title", "-t", required=True, help="Task title")
    create_parser.add_argument("--description", "-d", required=True, help="Task description")
    create_parser.add_argument(
        "--type",
        choices=[t.value for t in TaskType],
        default=TaskType.GENERIC,
        help="Task type",
    )
    create_parser.add_argument(
        "--status",
        choices=[s.value for s in TaskStatusEnum],
        default=TaskStatusEnum.PLANNED,
        help="Task status",
    )
    create_parser.add_argument(
        "--priority",
        choices=[p.value for p in TaskPriorityEnum],
        default=TaskPriorityEnum.MEDIUM,
        help="Task priority",
    )
    create_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    create_parser.add_argument("--parent", help="Parent task ID")
    create_parser.add_argument("--tags", help="Comma-separated list of tags")
    
    # Research-specific arguments
    create_parser.add_argument("--estimated-hours", type=float, help="Estimated hours to complete")
    create_parser.add_argument("--actual-hours", type=float, help="Actual hours spent")
    
    # Security-specific arguments
    create_parser.add_argument("--severity", help="Severity level")
    create_parser.add_argument("--affected-systems", help="Comma-separated list of affected systems")
    create_parser.add_argument("--discovered-by", help="Name of person who discovered the issue")
    
    # List tasks command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--type",
        choices=[t.value for t in TaskType],
        help="Filter by task type",
    )
    list_parser.add_argument(
        "--status",
        choices=[s.value for s in TaskStatusEnum],
        help="Filter by task status",
    )
    list_parser.add_argument(
        "--priority",
        choices=[p.value for p in TaskPriorityEnum],
        help="Filter by task priority",
    )
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    # Get task command
    get_parser = subparsers.add_parser("get", help="Get task details")
    get_parser.add_argument("task_id", help="Task ID")
    get_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    # Update task command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("task_id", help="Task ID")
    update_parser.add_argument("--title", "-t", help="Task title")
    update_parser.add_argument("--description", "-d", help="Task description")
    update_parser.add_argument(
        "--status",
        choices=[s.value for s in TaskStatusEnum],
        help="Task status",
    )
    update_parser.add_argument(
        "--priority",
        choices=[p.value for p in TaskPriorityEnum],
        help="Task priority",
    )
    update_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    
    # Research-specific arguments
    update_parser.add_argument("--estimated-hours", type=float, help="Estimated hours to complete")
    update_parser.add_argument("--actual-hours", type=float, help="Actual hours spent")
    
    # Security-specific arguments
    update_parser.add_argument("--severity", help="Severity level")
    update_parser.add_argument("--affected-systems", help="Comma-separated list of affected systems")
    update_parser.add_argument("--discovered-by", help="Name of person who discovered the issue")
    
    # Delete task command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")
    
    # Add note command
    note_parser = subparsers.add_parser("note", help="Add a note to a task")
    note_parser.add_argument("task_id", help="Task ID")
    note_parser.add_argument("note", help="Note content")
    
    # Add tag command
    add_tag_parser = subparsers.add_parser("add-tag", help="Add a tag to a task")
    add_tag_parser.add_argument("task_id", help="Task ID")
    add_tag_parser.add_argument("tag", help="Tag to add")
    
    # Remove tag command
    remove_tag_parser = subparsers.add_parser("remove-tag", help="Remove a tag from a task")
    remove_tag_parser.add_argument("task_id", help="Task ID")
    remove_tag_parser.add_argument("tag", help="Tag to remove")
    
    return parser


def handle_create_task(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the create task command."""
    # Parse tags
    tags = set()
    if args.tags:
        tags = {tag.strip() for tag in args.tags.split(",")}
    
    # Parse affected systems
    affected_systems = []
    if args.affected_systems:
        affected_systems = [sys.strip() for sys in args.affected_systems.split(",")]
    
    # Parse due date
    due_date = None
    if args.due:
        try:
            due_date = datetime.strptime(args.due, "%Y-%m-%d")
        except ValueError:
            return "Error: Due date must be in YYYY-MM-DD format"
    
    # Parse parent ID
    parent_id = None
    if args.parent:
        try:
            parent_id = UUID(args.parent)
        except ValueError:
            return "Error: Invalid parent task ID"
    
    # Create task
    try:
        task_id = task_manager.create_task(
            title=args.title,
            description=args.description,
            task_type=args.type,
            status=args.status,
            priority=args.priority,
            due_date=due_date,
            parent_id=parent_id,
            tags=tags,
            estimated_hours=args.estimated_hours,
            actual_hours=args.actual_hours,
            severity=args.severity,
            affected_systems=affected_systems,
            discovered_by=args.discovered_by,
        )
        return f"Task created with ID: {task_id}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_list_tasks(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the list tasks command."""
    # Apply filters
    tasks = []
    
    if args.type:
        tasks = task_manager.get_tasks_by_type(args.type)
    elif args.status:
        tasks = task_manager.get_tasks_by_status(args.status)
    elif args.tag:
        tasks = task_manager.get_tasks_by_tag(args.tag)
    else:
        tasks = task_manager.list_tasks()
    
    # Filter by priority if specified
    if args.priority and tasks:
        tasks = [task for task in tasks if task.priority == args.priority]
    
    if not tasks:
        return "No tasks found"
    
    if args.json:
        # Convert tasks to dictionaries and format as JSON
        tasks_data = [task.dict() for task in tasks]
        # Handle UUID and datetime serialization
        for task in tasks_data:
            task["id"] = str(task["id"])
            task["created_at"] = task["created_at"].isoformat()
            task["updated_at"] = task["updated_at"].isoformat()
            if task["due_date"]:
                task["due_date"] = task["due_date"].isoformat()
            if task["completed_at"]:
                task["completed_at"] = task["completed_at"].isoformat()
            if task["parent_id"]:
                task["parent_id"] = str(task["parent_id"])
            task["subtask_ids"] = [str(id) for id in task["subtask_ids"]]
        
        return json.dumps(tasks_data, indent=2)
    
    # Format as text
    result = []
    for i, task in enumerate(tasks, 1):
        result.append(f"{i}. [{task.status}] {task.title} (ID: {task.id})")
        result.append(f"   Priority: {task.priority}")
        if task.due_date:
            result.append(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
        result.append("")
    
    return "\n".join(result)


def handle_get_task(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the get task command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    task = task_manager.get_task(task_id)
    if not task:
        return f"Error: Task with ID {task_id} not found"
    
    return format_task_for_display(task.dict(), args.json)


def handle_update_task(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the update task command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    # Parse due date
    due_date = None
    if args.due:
        try:
            due_date = datetime.strptime(args.due, "%Y-%m-%d")
        except ValueError:
            return "Error: Due date must be in YYYY-MM-DD format"
    
    # Parse affected systems
    affected_systems = None
    if args.affected_systems:
        affected_systems = [sys.strip() for sys in args.affected_systems.split(",")]
    
    # Update task
    try:
        result = task_manager.update_task(
            task_id=task_id,
            title=args.title,
            description=args.description,
            status=args.status,
            priority=args.priority,
            due_date=due_date,
            estimated_hours=args.estimated_hours,
            actual_hours=args.actual_hours,
            severity=args.severity,
            affected_systems=affected_systems,
            discovered_by=args.discovered_by,
        )
        
        if result:
            return f"Task {task_id} updated successfully"
        else:
            return f"Error: Failed to update task {task_id}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_delete_task(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the delete task command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    result = task_manager.delete_task(task_id)
    if result:
        return f"Task {task_id} deleted successfully"
    else:
        return f"Error: Task with ID {task_id} not found"


def handle_add_note(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the add note command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    try:
        result = task_manager.add_task_note(task_id, args.note)
        if result:
            return f"Note added to task {task_id}"
        else:
            return f"Error: Failed to add note to task {task_id}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_add_tag(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the add tag command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    try:
        result = task_manager.add_task_tag(task_id, args.tag)
        if result:
            return f"Tag '{args.tag}' added to task {task_id}"
        else:
            return f"Error: Failed to add tag to task {task_id}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_remove_tag(args, task_manager: UnifiedTaskManager) -> str:
    """Handle the remove tag command."""
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    try:
        result = task_manager.remove_task_tag(task_id, args.tag)
        if result:
            return f"Tag '{args.tag}' removed from task {task_id}"
        else:
            return f"Error: Tag '{args.tag}' not found on task {task_id}"
    except ValueError as e:
        return f"Error: {str(e)}"


def execute_command(args, task_manager: UnifiedTaskManager) -> str:
    """Execute a command based on the parsed arguments."""
    if args.command == "create":
        return handle_create_task(args, task_manager)
    elif args.command == "list":
        return handle_list_tasks(args, task_manager)
    elif args.command == "get":
        return handle_get_task(args, task_manager)
    elif args.command == "update":
        return handle_update_task(args, task_manager)
    elif args.command == "delete":
        return handle_delete_task(args, task_manager)
    elif args.command == "note":
        return handle_add_note(args, task_manager)
    elif args.command == "add-tag":
        return handle_add_tag(args, task_manager)
    elif args.command == "remove-tag":
        return handle_remove_tag(args, task_manager)
    else:
        return "Error: Unknown command"


def main(args=None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Show help if no command specified
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    # Initialize task manager
    task_manager = UnifiedTaskManager()
    
    # Execute command
    try:
        result = execute_command(parsed_args, task_manager)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())