import json
import os
import tempfile
import pytest
import cli

def test_scaffold_protocol(tmp_path, capsys):
    file_path = tmp_path / "spec.json"
    cli.scaffold_protocol(str(file_path))
    captured = capsys.readouterr()
    assert "Scaffolded protocol spec to" in captured.out
    # Check file content
    content = json.loads(file_path.read_text())
    assert content == {
        'states': [],
        'transitions': [],
        'guards': [],
        'on_enter': {},
        'global_hooks': {},
        'history': {}
    }

def test_visualize_spec(tmp_path, capsys):
    spec = {
        'states': ['A', 'B'],
        'transitions': [{'name': 'A→B', 'from': 'A', 'to': 'B', 'action': 'act'}],
        'guards': [],
        'on_enter': {},
        'global_hooks': {},
        'history': {}
    }
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(spec))
    cli.visualize_spec(str(spec_file))
    captured = capsys.readouterr()
    assert 'digraph G' in captured.out
    assert '"A" -> "B" [label="A→B"]' in captured.out
