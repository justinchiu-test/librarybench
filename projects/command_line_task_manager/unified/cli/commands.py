"""
Command-line interface commands for the unified task manager.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from cli.task_manager import UnifiedTaskManager, TaskType
from cli.enums import TaskStatusEnum, TaskPriorityEnum


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
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


def format_task_for_display(task: Dict[str, Any], json_output: bool = False) -> str:
    """
    Format a task for display.
    
    Args:
        task: Task data
        json_output: Whether to output in JSON format
        
    Returns:
        str: Formatted task string
    """
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


def handle_create_task(args, task_manager: UnifiedTaskManager) -> str:
    """
    Handle the create task command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the list tasks command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the get task command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
    try:
        task_id = UUID(args.task_id)
    except ValueError:
        return "Error: Invalid task ID"
    
    task = task_manager.get_task(task_id)
    if not task:
        return f"Error: Task with ID {task_id} not found"
    
    return format_task_for_display(task.dict(), args.json)


def handle_update_task(args, task_manager: UnifiedTaskManager) -> str:
    """
    Handle the update task command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the delete task command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the add note command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the add tag command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Handle the remove tag command.
    
    Args:
        args: Command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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
    """
    Execute a command based on the parsed arguments.
    
    Args:
        args: Parsed command arguments
        task_manager: Task manager instance
        
    Returns:
        str: Command result message
    """
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