import sys
import yaml
import tempfile
from robotfsm import cli, reset_machine, STATE_MACHINE

def test_scaffold(capsys):
    sys.argv = ['robotfsm', 'scaffold', 'mytpl']
    cli()
    captured = capsys.readouterr()
    assert "# Template: mytpl" in captured.out
    data = yaml.safe_load(captured.out.splitlines(1)[1])
    assert data['template'] == 'mytpl'
    assert 'states' in data and 'transitions' in data

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
