"""
Command-line interface for managing the workflow system.
"""
import click
from .manager import WorkflowManager
from .task import Task
from .auth import authenticate

# Single global manager for demo
manager = WorkflowManager()
CURRENT_TOKEN = {"value": None}

@click.group()
def cli():
    """Workflow management CLI."""
    pass

@cli.command()
@click.option('--token', required=True, help="Authentication token")
@click.argument('task_id')
@click.argument('priority', type=int)
def add_task(token, task_id, priority):
    """Add a new dummy task that succeeds."""
    auth = authenticate(token)
    @auth
    def _inner():
        t = Task(task_id, func=lambda: None, priority=priority)
        manager.add_task(t)
        click.echo(f"Task {task_id} added with priority {priority}")
    _inner()

@cli.command()
@click.option('--token', required=True, help="Authentication token")
def run(token):
    """Run all tasks."""
    auth = authenticate(token)
    @auth
    def _inner():
        manager.run_all()
        click.echo("All tasks executed.")
    _inner()

@cli.command()
@click.option('--token', required=True, help="Authentication token")
def list_states(token):
    """List task states."""
    auth = authenticate(token)
    @auth
    def _inner():
        states = manager.get_all_states()
        for tid, state in states.items():
            click.echo(f"{tid}: {state}")
    _inner()

@cli.command()
@click.option('--token', required=True, help="Authentication token")
@click.argument('interval', type=float)
def schedule(token, interval):
    """Start scheduler with given interval (seconds)."""
    auth = authenticate(token)
    @auth
    def _inner():
        from .scheduler import Scheduler
        sched = Scheduler(interval, manager.run_all)
        sched.start()
        click.echo(f"Scheduler started with interval {interval}s.")
    _inner()
