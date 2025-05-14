import pytest
from cli_tools import scaffold_gait_machine, run_step_simulation, export_timing_diagram

def test_scaffold_gait_machine():
    data = scaffold_gait_machine()
    assert isinstance(data, dict)
    assert "states" in data and "idle" in data["states"]
    assert any(t["name"]=="start_walk" for t in data["transitions"])

def test_run_step_simulation():
    actions = ["a", "b", "c"]
    logs = run_step_simulation(actions)
    assert len(logs) == 3
    assert logs[0] == "Step 0: a"

def test_export_timing_diagram():
    actions = [1,2,3]
    s = export_timing_diagram(actions)
    assert '"timing"' in s
    assert '1' in s
