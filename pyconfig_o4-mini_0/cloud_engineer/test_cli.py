import pytest
from config_loader.cli import prompt_missing

def test_prompt_missing(monkeypatch):
    inputs = iter(['foo', 'bar'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    cfg = {'a': None}
    result = prompt_missing(cfg, ['a', 'b'])
    assert result['a'] == 'foo'
    assert result['b'] == 'bar'
