import pytest
from cli_framework.prompt import prompt_interactive, secure_prompt

def test_prompt_yes_no(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: 'yes')
    assert prompt_interactive("Proceed", choices=['yes','no'], type=str) == 'yes'

def test_prompt_default(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: '')
    assert prompt_interactive("Number", choices=None, type=int, default=5) == 5

def test_secure_prompt(monkeypatch):
    monkeypatch.setattr('getpass.getpass', lambda prompt: 'secret')
    val = secure_prompt("Token: ")
    assert val == 'secret'
