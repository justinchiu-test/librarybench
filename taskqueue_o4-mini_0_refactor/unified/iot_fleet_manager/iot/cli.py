import click
from .scheduler import DelayedScheduler
from .dead_letter_queue import DeadLetterQueue
from .audit_logging import AuditLogger

_scheduler = DelayedScheduler()
_dead_letter = DeadLetterQueue()
_audit_logger = AuditLogger('audit.log')

@click.group()
def cli():
    pass

@cli.command()
@click.argument('campaign_id')
@click.argument('delay', type=float)
def enqueue(campaign_id, delay):
    """Enqueue new campaign"""
    def dummy_task():
        pass
    _scheduler.schedule(campaign_id, dummy_task, delay)
    _audit_logger.log('enqueue', {'campaign_id': campaign_id, 'delay': delay})
    click.echo(f"Enqueued campaign {campaign_id} with delay {delay}")

@cli.command(name='queue_depth')
def queue_depth():
    """View queue depth"""
    depth = len(_scheduler._timers)
    click.echo(depth)

@cli.command()
def replay():
    """Replay failed updates"""
    tasks = _dead_letter.get_all()
    for task in tasks:
        click.echo(f"Replaying {task}")
    _dead_letter.clear()
    _audit_logger.log('replay', {'tasks': tasks})

@cli.command(name='tail_logs')
@click.argument('n', type=int, default=10)
def tail_logs(n):
    """Tail audit logs"""
    logs = _audit_logger.read_logs()
    for entry in logs[-n:]:
        click.echo(entry)
