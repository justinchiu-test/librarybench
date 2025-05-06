import click

from manager import Manager
from scheduler import Scheduler

@click.group()
def cli():
    """Task scheduler CLI."""
    pass

@cli.command()
@click.option("--token", required=True, help="API token")
@click.argument("name")
@click.argument("cpus", type=int)
def add_task(name, cpus, token):
    """
    Add a new task with a given NAME and number of CPU slots (CPUS).
    """
    mgr = Manager(token)
    mgr.add_task(name, cpus)

@cli.command()
@click.option("--token", required=True, help="API token")
def run(token):
    """
    Run all pending tasks.
    """
    mgr = Manager(token)
    sched = Scheduler(mgr)
    sched.run()

@cli.command()
@click.option("--token", required=True, help="API token")
def list_states(token):
    """
    List the current state of all tasks.
    """
    mgr = Manager(token)
    states = mgr.list_states()
    for name, state in states.items():
        click.echo(f"{name}: {state}")
