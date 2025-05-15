import sys
# Ensure local robotics_engineer package is loaded before any installed one
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import robotics_engineer.yaml as yaml
import tempfile
from robotics_engineer.robotfsm import cli, reset_machine, STATE_MACHINE

def test_scaffold(capsys):
    sys.argv = ['robotfsm', 'scaffold', 'mytpl']
    cli()
    captured = capsys.readouterr()
    # Ensure the scaffold command outputs the template header
    assert "# Template: mytpl" in captured.out

def test_run_command(tmp_path, capsys):
    # create a machine yaml
    content = {
        'states': ['A', 'B'],
        'transitions': [
            {'name': 't', 'src': 'A', 'dst': 'B', 'trigger': 'go'}
        ]
    }
    p = tmp_path / "m.yaml"
    p.write_text(yaml.dump(content))
    sys.argv = ['robotfsm', 'run', str(p)]
    cli()
    captured = capsys.readouterr()
    assert "Machine loaded with 2 states and 1 transitions" in captured.out
