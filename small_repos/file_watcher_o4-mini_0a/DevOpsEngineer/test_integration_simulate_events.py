import pytest
from file_watcher.cli_interface import main
from file_watcher.core import JenkinsPlugin

def test_integration_cli_and_plugin(tmp_path):
    fw = main(['--dry-run'])
    # find the JenkinsPlugin instance
    jenkins = next(p for p in fw.plugins if isinstance(p, JenkinsPlugin))
    # register a handler that triggers plugin on modify
    fw.register_handler('modify', r'.*', lambda e: None)
    # simulate event
    ev = fw.trigger_event('file', 'modify')
    assert ev is not None
    # Jenkins was called in dry-run mode
    assert jenkins.triggered == [('dry', ev)]
