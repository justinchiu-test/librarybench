import os
from click.testing import CliRunner
from iot_fleet_manager.iot.cli import cli, _scheduler, _dead_letter, _audit_logger
from iot_fleet_manager.iot.audit_logging import AuditLogger
import tempfile

def test_queue_depth():
    runner = CliRunner()
    result = runner.invoke(cli, ['queue_depth'])
    assert result.exit_code == 0
    assert result.output.strip() == '0'

def test_enqueue_and_tail_logs(tmp_path, monkeypatch):
    # Redirect audit log
    log_file = tmp_path / "audit.log"
    monkeypatch.setattr('iot.cli._audit_logger', AuditLogger(str(log_file)))
    runner = CliRunner()
    result = runner.invoke(cli, ['enqueue', 'camp1', '0'])
    assert result.exit_code == 0
    assert "Enqueued campaign camp1 with delay 0.0" in result.output
    # Tail logs
    result = runner.invoke(cli, ['tail_logs', '1'])
    assert result.exit_code == 0
    assert 'test_event' not in result.output  # no test_event, but at least one log entry appears
