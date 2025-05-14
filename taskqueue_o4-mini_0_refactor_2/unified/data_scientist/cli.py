import click
from data_scientist.ml_pipeline.orchestrator import Orchestrator

orch = Orchestrator()

@click.group()
def cli():
    pass

@cli.command()
@click.argument('func')
@click.option('--param', '-p', multiple=True)
def enqueue(func, param):
    click.echo(f"Enqueued {func} with params {param}")

@cli.command(name='list')
def _list():
    statuses = orch.list_statuses()
    for tid, status in statuses.items():
        click.echo(f"{tid}: {status}")

@cli.command()
@click.argument('task_id')
def requeue(task_id):
    ok = orch.requeue_failed(task_id)
    if ok:
        click.echo(f"Requeued {task_id}")
    else:
        click.echo(f"Cannot requeue {task_id}")

@cli.command(name='tail_logs')
@click.option('--lines', '-n', default=10)
def tail_logs(lines):
    # Delegate to root-level cli.orch so tests can patch it
    import cli as root_cli
    if hasattr(root_cli, 'orch') and root_cli.orch is not None:
        logs = root_cli.orch.tail_logs(lines)
    else:
        # Fallback to module orch
        logs = orch.tail_logs(lines)
    click.echo(logs)
