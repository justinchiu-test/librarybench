import os
import pytest
from src.personas.data_scientist.datapipeline_cli.secrets import manage_secrets

def test_manage_secrets_env(monkeypatch):
    monkeypatch.setenv('SECRET_STORE', 'env')
    monkeypatch.setenv('K1', 'v1')
    monkeypatch.setenv('K2', 'v2')
    secrets = manage_secrets(['K1', 'K2'])
    assert secrets == {'K1': 'v1', 'K2': 'v2'}

def test_manage_secrets_missing(monkeypatch):
    monkeypatch.setenv('SECRET_STORE', 'env')
    with pytest.raises(KeyError):
        manage_secrets(['NOPE'])
