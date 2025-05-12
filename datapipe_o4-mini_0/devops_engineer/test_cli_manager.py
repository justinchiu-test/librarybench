from pipeline.cli_manager import CLIManager

def test_cli_commands():
    manager = CLIManager()
    assert manager.run(['deploy']) == 'deploy'
    assert manager.run(['upgrade']) == 'upgrade'
    assert manager.run(['rollback']) == 'rollback'
    assert manager.run(['debug']) == 'debug'
