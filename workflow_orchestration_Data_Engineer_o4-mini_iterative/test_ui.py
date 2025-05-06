import pytest
from click.testing import CliRunner
import workflow.ui as ui
from workflow.auth import USER_TOKENS

TOKEN = list(USER_TOKENS.values())[0]

@pytest.fixture(autouse=True)
def reset_manager():
    # reset global manager state
    ui.manager = ui.manager.__class__()  # new instance
    return

def test_add_and_list_states():
    runner = CliRunner()
    result = runner.invoke(ui.cli, ["add_task", "--token", TOKEN, "task1", "2"])
    assert result.exit_code == 0
    result2 = runner.invoke(ui.cli, ["list_states", "--token", TOKEN])
    assert "task1: pending" in result2.output

def test_run_and_list_states():
    runner = CliRunner()
    runner.invoke(ui.cli, ["add_task", "--token", TOKEN, "task2", "1"])
    runner.invoke(ui.cli, ["run", "--token", TOKEN])
    result = runner.invoke(ui.cli, ["list_states", "--token", TOKEN])
    assert "task2: success" in result.output

def test_schedule_command():
    runner = CliRunner()
    result = runner.invoke(ui.cli, ["schedule", "--token", TOKEN, "0.01"])
    assert result.exit_code == 0
    assert "Scheduler started" in result.output
