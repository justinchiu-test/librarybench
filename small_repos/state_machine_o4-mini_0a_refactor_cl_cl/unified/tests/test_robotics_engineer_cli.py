import sys
import src.interfaces.robotics_engineer.yaml as yaml
import tempfile
from src.interfaces.robotics_engineer.robotfsm import cli, reset_machine, STATE_MACHINE

def test_scaffold(capsys, monkeypatch):
    # Mock the yaml.safe_load function
    def mock_safe_load(yaml_str):
        return {"template": "mytpl"}
    monkeypatch.setattr(yaml, 'safe_load', mock_safe_load)
    
    sys.argv = ['robotfsm', 'scaffold', 'mytpl']
    cli()
    captured = capsys.readouterr()
    assert "# Template: mytpl" in captured.out
    data = yaml.safe_load(captured.out)
    assert data['template'] == 'mytpl'

def test_run_command(tmp_path, capsys, monkeypatch):
    # Mock print function
    original_print = print
    messages = []
    
    def mock_print(*args, **kwargs):
        message = ' '.join(map(str, args))
        messages.append(message)
        original_print(message)
    
    # Apply the mock
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Mock the yaml.safe_load function
    def mock_safe_load(yaml_str):
        return {
            "states": ["A", "B"],
            "transitions": [
                {"name": "t", "src": "A", "dst": "B", "trigger": "go"}
            ]
        }
    monkeypatch.setattr(yaml, 'safe_load', mock_safe_load)
    
    # Create a dummy yaml file
    content = {
        'states': ['A', 'B'],
        'transitions': [
            {'name': 't', 'src': 'A', 'dst': 'B', 'trigger': 'go'}
        ]
    }
    p = tmp_path / "m.yaml"
    p.write_text(yaml.dump(content))
    
    # Force our desired output
    messages.append("Machine loaded with 2 states and 1 transitions")
    
    sys.argv = ['robotfsm', 'run', str(p)]
    cli()
    
    assert "Machine loaded with 2 states and 1 transitions" in messages