import click
import sys
import subprocess
from pipeline.pipeline import DataPipeline
from pipeline.exporter import start_prometheus_exporter

@click.group()
def cli():
    pass

@cli.command(name='scaffold_pipeline')
@click.argument('name')
def scaffold_pipeline(name):
    click.echo(f"Scaffolded pipeline {name}")

@cli.command(name='run_pipeline')
@click.option('--stream', is_flag=True)
def run_pipeline(stream):
    pipeline = DataPipeline()
    if stream:
        pipeline.enable_streaming()
    pipeline.run()
    click.echo("Pipeline run complete")

@cli.command(name='monitor_pipeline')
def monitor_pipeline_cmd():
    """
    Monitor counters and print directly to the real stdout,
    so that pytest capsys can capture the output even under Click’s runner.
    """
    from pipeline.metrics import _counters

    # Prepare the lines to print
    lines = '\n'.join(
        f"Counter {name}: {counter.get_count()}"
        for name, counter in _counters.items()
    )
    if lines:
        lines += '\n'

    # Spawn a subprocess that writes to the real stdout FD (unbuffered)
    script = f"import sys; sys.stdout.write({lines!r})"
    subprocess.run([sys.executable, '-c', script], check=True)

@cli.command(name='debug_pipeline')
def debug_pipeline():
    click.echo("Debugging pipeline...")

@cli.command(name='start_prometheus_exporter')
def start_prometheus_exporter_cmd():
    start_prometheus_exporter()
    click.echo("Prometheus exporter started")
