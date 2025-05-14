from click.testing import CliRunner
from data_scientist.cli import cli

def test_cli_enqueue():
    runner = CliRunner()
    result = runner.invoke(cli, ['enqueue', 'taskname', '-p', 'a=1'])
    assert result.exit_code == 0
    assert "Enqueued taskname" in result.output

def test_cli_list_empty():
    runner = CliRunner()
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0

def test_cli_requeue():
    runner = CliRunner()
    result = runner.invoke(cli, ['requeue', 'nonexistent'])
    assert result.exit_code == 0
    assert "Cannot requeue" in result.output

def test_cli_tail_logs(tmp_path, monkeypatch):
    # simulate empty logs
    from data_scientist.ml_pipeline.orchestrator import Orchestrator
    orch = Orchestrator(log_file=str(tmp_path / "audit.log"))
    monkeypatch.setattr('data_scientist.cli.orch', orch)
    runner = CliRunner()
    result = runner.invoke(cli, ['tail_logs'])
    assert result.exit_code == 0
    assert result.output == "\n"
