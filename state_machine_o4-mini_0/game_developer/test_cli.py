import os
import json
import pytest
from statemachine_cli import scaffold_machine, visualize_machine
from statemachine import StateMachine

def test_scaffold(tmp_path, monkeypatch):
    cwd = tmp_path
    monkeypatch.chdir(cwd)
    filename = scaffold_machine("mymachine")
    assert os.path.exists(cwd / filename)
    content = (cwd / filename).read_text()
    assert "create_machine" in content

def test_visualize_cli(tmp_path, monkeypatch):
    cwd = tmp_path
    monkeypatch.chdir(cwd)
    # create a machine and export json
    m = StateMachine()
    m.define_transition("go", "A", "B", "go")
    m.current_state = "A"
    json_file = cwd / "m.json"
    json_file.write_text(m.export_machine(format="json"))
    out = visualize_machine(str(json_file))
    assert os.path.exists(cwd / out)
    # check dot content
    content = (cwd / out).read_text()
    assert '"A" -> "B"' in content
