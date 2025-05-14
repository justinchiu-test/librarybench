from click.testing import CliRunner
import pytest
from pipeline.cli import cli

def test_scaffold_pipeline():
    runner = CliRunner()
    result = runner.invoke(cli, ['scaffold_pipeline', 'test'])
    assert result.exit_code == 0
    assert "Scaffolded pipeline test" in result.output

def test_run_pipeline_stream():
    runner = CliRunner()
    result = runner.invoke(cli, ['run_pipeline', '--stream'])
    assert result.exit_code == 0
    assert "Pipeline run complete" in result.output

def test_monitor_pipeline(capsys):
    # ensure some counters
    from pipeline.metrics import create_counter
    create_counter('x').inc()
    runner = CliRunner()
    runner.invoke(cli, ['monitor_pipeline'])
    captured = capsys.readouterr()
    assert "Counter x: 1" in captured.out

def test_debug_pipeline():
    runner = CliRunner()
    result = runner.invoke(cli, ['debug_pipeline'])
    assert result.exit_code == 0
    assert "Debugging pipeline" in result.output

def test_start_prometheus_exporter(monkeypatch):
    called = []
    monkeypatch.setattr('pipeline.exporter.start_http_server', lambda port=0: called.append(port))
    runner = CliRunner()
    result = runner.invoke(cli, ['start_prometheus_exporter'])
    assert result.exit_code == 0
    assert called, "start_http_server was not called"
    assert "Prometheus exporter started" in result.output
