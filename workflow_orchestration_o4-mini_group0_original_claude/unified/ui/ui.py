"""
Command-line and web interfaces for the unified workflow orchestration system.
"""
import argparse
import cmd
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from unified.task_manager import TaskManager
from unified.workflow.workflow import WorkflowManager
from unified.task import Task, TaskState
from unified.logger import configure_logger
from unified.utils import generate_id


class WorkflowCLI(cmd.Cmd):
    """
    Command-line interface for workflow management.
    """
    intro = "Welcome to the Workflow Orchestration CLI. Type help or ? to list commands.\n"
    prompt = "workflow> "
    
    def __init__(self, task_manager=None, workflow_manager=None):
        """
        Initialize the CLI with task and workflow managers.
        
        :param task_manager: TaskManager instance (created if not provided)
        :param workflow_manager: WorkflowManager instance (created if not provided)
        """
        super().__init__()
        self.task_manager = task_manager or TaskManager()
        self.workflow_manager = workflow_manager or WorkflowManager()
        self.logger = configure_logger("cli")
    
    def do_list_tasks(self, arg):
        """
        List all tasks: list_tasks
        """
        try:
            metadata = self.task_manager.get_all_task_metadata()
            if not metadata:
                print("No tasks found.")
                return
            
            print(f"Found {len(metadata)} tasks:")
            for task_id, meta in metadata.items():
                status = meta.get("status", "unknown")
                priority = meta.get("priority", "unknown")
                print(f"  {task_id}: status={status}, priority={priority}")
        except Exception as e:
            print(f"Error listing tasks: {str(e)}")
    
    def do_task_info(self, arg):
        """
        Show task details: task_info <task_id>
        """
        if not arg:
            print("Error: Task ID required.")
            return
        
        try:
            metadata = self.task_manager.get_task_metadata(arg)
            if not metadata:
                print(f"Task '{arg}' not found.")
                return
            
            print(f"Task {arg}:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error getting task info: {str(e)}")
    
    def do_cancel_task(self, arg):
        """
        Cancel a task: cancel_task <task_id>
        """
        if not arg:
            print("Error: Task ID required.")
            return
        
        try:
            canceled = self.task_manager.cancel_task(arg)
            if canceled:
                print(f"Task '{arg}' canceled.")
            else:
                print(f"Failed to cancel task '{arg}'. It may not exist or is not in a cancelable state.")
        except Exception as e:
            print(f"Error canceling task: {str(e)}")
    
    def do_list_workflows(self, arg):
        """
        List all workflows: list_workflows
        """
        try:
            workflows = self.workflow_manager.list_workflows()
            if not workflows:
                print("No workflows found.")
                return
            
            print(f"Found {len(workflows)} workflows:")
            for wf in workflows:
                wid = wf["workflow_id"]
                name = wf["name"]
                version = wf["version"]
                task_count = wf["task_count"]
                print(f"  {wid}: {name} (v{version}), {task_count} tasks")
        except Exception as e:
            print(f"Error listing workflows: {str(e)}")
    
    def do_workflow_info(self, arg):
        """
        Show workflow details: workflow_info <workflow_id>
        """
        if not arg:
            print("Error: Workflow ID required.")
            return
        
        try:
            workflow = self.workflow_manager.get_workflow(arg)
            if not workflow:
                print(f"Workflow '{arg}' not found.")
                return
            
            print(f"Workflow {arg}:")
            print(f"  Name: {workflow['name']}")
            print(f"  Version: {workflow['version']}")
            print(f"  Description: {workflow['description']}")
            print(f"  Tasks: {workflow['task_count']}")
            print(f"  Status: {workflow['status']}")
            print(f"  Created: {time.ctime(workflow['created_at'])}")
            
            if workflow['last_run_at']:
                print(f"  Last run: {time.ctime(workflow['last_run_at'])}")
            
            if workflow['task_count'] > 0:
                print("\nTasks:")
                for task_id, task in workflow['tasks'].items():
                    print(f"  {task_id}: {task['state']}")
        except Exception as e:
            print(f"Error getting workflow info: {str(e)}")
    
    def do_run_workflow(self, arg):
        """
        Run a workflow: run_workflow <workflow_id>
        """
        if not arg:
            print("Error: Workflow ID required.")
            return
        
        try:
            print(f"Running workflow '{arg}'...")
            result = self.workflow_manager.run_workflow(arg)
            
            if not result:
                print(f"Workflow '{arg}' not found.")
                return
            
            if result["success"]:
                print(f"Workflow '{arg}' completed successfully.")
            else:
                print(f"Workflow '{arg}' failed.")
            
            print("\nTask results:")
            for task_id, task_result in result["task_results"].items():
                status = task_result["status"]
                success = "succeeded" if task_result["success"] else "failed"
                print(f"  {task_id}: {status} ({success})")
                if not task_result["success"] and "error" in task_result:
                    print(f"    Error: {task_result['error']}")
        except Exception as e:
            print(f"Error running workflow: {str(e)}")
    
    def do_create_workflow(self, arg):
        """
        Create a new workflow: create_workflow <name> [description]
        """
        args = arg.split(maxsplit=1)
        if not args:
            print("Error: Workflow name required.")
            return
        
        name = args[0]
        description = args[1] if len(args) > 1 else ""
        
        try:
            workflow_id = self.workflow_manager.register_workflow(
                name=name,
                description=description
            )
            print(f"Created workflow '{name}' with ID: {workflow_id}")
        except Exception as e:
            print(f"Error creating workflow: {str(e)}")
    
    def do_add_task(self, arg):
        """
        Add a simple task to a workflow: add_task <workflow_id> <task_name> <python_code>
        
        Example: add_task my-workflow-id my-task "return 42"
        """
        args = arg.split(maxsplit=2)
        if len(args) < 3:
            print("Error: Workflow ID, task name, and Python code required.")
            return
        
        workflow_id, task_name, code = args
        
        try:
            # Create function from code
            function_locals = {}
            exec(f"def task_function():\n    {code}", globals(), function_locals)
            func = function_locals["task_function"]
            
            # Create task
            task = Task(
                task_id=task_name,
                func=func
            )
            
            # Add to workflow
            success = self.workflow_manager.add_task_to_workflow(workflow_id, task)
            
            if success:
                print(f"Added task '{task_name}' to workflow '{workflow_id}'")
            else:
                print(f"Failed to add task to workflow '{workflow_id}'")
        except Exception as e:
            print(f"Error adding task: {str(e)}")
    
    def do_schedule_workflow(self, arg):
        """
        Schedule a workflow: schedule_workflow <workflow_id> <interval_seconds>
        """
        args = arg.split()
        if len(args) < 2:
            print("Error: Workflow ID and interval required.")
            return
        
        try:
            workflow_id = args[0]
            interval = float(args[1])
            
            schedule_id = self.workflow_manager.schedule_workflow(
                workflow_id=workflow_id,
                interval_seconds=interval
            )
            
            if schedule_id:
                print(f"Scheduled workflow '{workflow_id}' every {interval} seconds.")
                print(f"Schedule ID: {schedule_id}")
            else:
                print(f"Failed to schedule workflow '{workflow_id}'")
        except ValueError:
            print("Error: Interval must be a number.")
        except Exception as e:
            print(f"Error scheduling workflow: {str(e)}")
    
    def do_exit(self, arg):
        """
        Exit the CLI: exit
        """
        print("Shutting down...")
        self.task_manager.shutdown()
        return True
    
    def do_quit(self, arg):
        """
        Exit the CLI: quit
        """
        return self.do_exit(arg)


def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(description="Workflow Orchestration CLI")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--log-level", default="info", help="Log level (debug, info, warning, error)")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level_map = {
        "debug": 10,
        "info": 20,
        "warning": 30,
        "error": 40
    }
    log_level = log_level_map.get(args.log_level.lower(), 20)
    
    logger = configure_logger(
        name="cli",
        log_level=log_level,
        log_file=args.log_file
    )
    
    # Start the CLI
    cli = WorkflowCLI()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        cli.task_manager.shutdown()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        print(f"Error: {str(e)}")
        cli.task_manager.shutdown()


if __name__ == "__main__":
    main()


# Web UI functions (to be integrated with the API)

def create_workflow_form():
    """
    Generate HTML for creating a workflow.
    """
    return """
    <h2>Create Workflow</h2>
    <form action="/api/workflows" method="post">
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div>
            <label for="description">Description:</label>
            <textarea id="description" name="description"></textarea>
        </div>
        <button type="submit">Create</button>
    </form>
    """

def create_task_form(workflow_id):
    """
    Generate HTML for creating a task within a workflow.
    
    :param workflow_id: Workflow ID
    :return: HTML form
    """
    return f"""
    <h2>Add Task to Workflow</h2>
    <form action="/api/workflows/{workflow_id}/tasks" method="post">
        <div>
            <label for="task_id">Task ID:</label>
            <input type="text" id="task_id" name="task_id">
        </div>
        <div>
            <label for="function_code">Function Code:</label>
            <textarea id="function_code" name="function_code" required></textarea>
        </div>
        <div>
            <label for="priority">Priority:</label>
            <input type="number" id="priority" name="priority" value="5">
        </div>
        <div>
            <label for="timeout">Timeout (seconds):</label>
            <input type="number" id="timeout" name="timeout" min="0" step="0.1">
        </div>
        <div>
            <label for="max_retries">Max Retries:</label>
            <input type="number" id="max_retries" name="max_retries" value="0" min="0">
        </div>
        <div>
            <label for="retry_delay_seconds">Retry Delay (seconds):</label>
            <input type="number" id="retry_delay_seconds" name="retry_delay_seconds" value="1.0" min="0" step="0.1">
        </div>
        <div>
            <label for="dependencies">Dependencies (comma-separated task IDs):</label>
            <input type="text" id="dependencies" name="dependencies">
        </div>
        <button type="submit">Add Task</button>
    </form>
    """

def render_workflow_list(workflows):
    """
    Generate HTML for the workflow list.
    
    :param workflows: List of workflow dictionaries
    :return: HTML content
    """
    html = "<h2>Workflows</h2>"
    
    if not workflows:
        html += "<p>No workflows found.</p>"
        return html
    
    html += "<ul>"
    for wf in workflows:
        html += f"""
        <li>
            <strong>{wf['name']}</strong> (ID: {wf['workflow_id']}, Version: {wf['version']})
            <p>{wf['description']}</p>
            <p>Tasks: {wf['task_count']}, Status: {wf['status']}</p>
            <a href="/workflows/{wf['workflow_id']}">View</a> |
            <a href="/workflows/{wf['workflow_id']}/run">Run</a> |
            <a href="/workflows/{wf['workflow_id']}/tasks/new">Add Task</a> |
            <a href="/workflows/{wf['workflow_id']}/schedule">Schedule</a>
        </li>
        """
    html += "</ul>"
    
    return html

def render_task_list(tasks):
    """
    Generate HTML for the task list.
    
    :param tasks: List of task dictionaries
    :return: HTML content
    """
    html = "<h2>Tasks</h2>"
    
    if not tasks:
        html += "<p>No tasks found.</p>"
        return html
    
    html += "<table border='1'>"
    html += "<tr><th>ID</th><th>Status</th><th>Priority</th><th>Execution Time</th><th>Actions</th></tr>"
    
    for task in tasks:
        execution_time = task.get('execution_time')
        execution_str = f"{execution_time:.2f}s" if execution_time else "N/A"
        
        html += f"""
        <tr>
            <td>{task['task_id']}</td>
            <td>{task['status']}</td>
            <td>{task['priority']}</td>
            <td>{execution_str}</td>
            <td>
                <a href="/tasks/{task['task_id']}">View</a>
                {' | <a href="/tasks/' + task['task_id'] + '/cancel">Cancel</a>' if task['status'] == 'running' else ''}
            </td>
        </tr>
        """
    
    html += "</table>"
    return html