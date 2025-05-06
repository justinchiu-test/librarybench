import click
from .manager import WorkflowManager
from .task import Task
import utils

# Single global manager for demo
manager = WorkflowManager()

@click.group()
def cli():
    pass


@cli.command()
@click.option('--token', required=True)
@click.argument('task_id')
@click.argument('priority', type=int)
def add_task(token, task_id, priority):
    def action():
        t = Task(task_id, func=lambda: None, priority=priority)
        manager.add_task(t)
        click.echo(f"Task {task_id} added with priority {priority}")
    utils.auth_and_execute(token, action)


@cli.command()
@click.option('--token', required=True)
def run(token):
    def action():
        manager.run_all()
        click.echo("All tasks executed.")
    utils.auth_and_execute(token, action)


@cli.command()
@click.option('--token', required=True)
def list_states(token):
    def action():
        states = manager.get_all_states()
        for tid, state in states.items():
            click.echo(f"{tid}: {state}")
    utils.auth_and_execute(token, action)


@cli.command()
@click.option('--token', required=True)
@click.argument('interval', type=float)
def schedule(token, interval):
    def action():
        from .scheduler import Scheduler
        sched = Scheduler(interval, manager.run_all)
        sched.start()
        click.echo(f"Scheduler started with interval {interval}s.")
    utils.auth_and_execute(token, action)
