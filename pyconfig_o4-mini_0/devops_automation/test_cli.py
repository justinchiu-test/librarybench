import pytest
from config_manager.cli import InteractiveCLI

def test_prompt_with_input(monkeypatch):
    inputs = iter(["hello"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    cli = InteractiveCLI()
    assert cli.prompt("p", "Enter", "def") == "hello"

def test_prompt_default(monkeypatch):
    inputs = iter([""])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    cli = InteractiveCLI()
    assert cli.prompt("p", "Enter", "def") == "def"
