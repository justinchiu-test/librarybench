import os
from feature_pipeline.cli import CLIManager

def test_scaffold_experiment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mgr = CLIManager()
    path = mgr.scaffold_experiment("exp1")
    assert path == "experiments/exp1"
    assert os.path.isdir(path)

def test_run_pipeline_locally(capsys):
    mgr = CLIManager()
    def pipeline():
        return "done"
    result = mgr.run_pipeline_locally(pipeline, verbose=True)
    captured = capsys.readouterr()
    assert "Running in verbose mode" in captured.out
    assert result == "done"
