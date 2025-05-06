import pytest
from Research_Scientist.workflow.cli import CLI
from Research_Scientist.workflow.models import TaskState

def sample_task(x):
    return x * x

def test_cli_add_and_run(monkeypatch):
    cli = CLI()
    token = 'abc123'
    cli.register_user(token)
    # add a task
    cli.add_task(id='c1', func=sample_task, args=(4,), priority=5,
                 max_retries=0, retry_delay=0, token=token)
    # monkeypatch sleep to no-op
    import time
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    # run tasks
    cli.run(token=token)
    t = cli.task_manager.get_task('c1')
    assert t.state == TaskState.SUCCESS
    assert t.result == 16

def test_cli_auth_missing():
    cli = CLI()
    with pytest.raises(Exception):
        cli.add_task(id='x', func=lambda: None, token='bad')
    with pytest.raises(Exception):
        cli.run(token='bad')
