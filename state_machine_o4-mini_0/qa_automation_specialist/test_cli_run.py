import sys
import pytest
import cli_run

def test_list_scenarios(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '--list-scenarios'])
    cli_run.cli_run_tests()
    captured = capsys.readouterr()
    assert 'sample' in captured.out

def test_run_scenario_success(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '--scenario', 'sample'])
    cli_run.cli_run_tests()
    captured = capsys.readouterr()
    assert 'Result: sample_result' in captured.out

def test_run_scenario_failure(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '--scenario', 'unknown'])
    cli_run.cli_run_tests()
    captured = capsys.readouterr()
    assert 'Error:' in captured.out
