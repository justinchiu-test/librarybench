from cli_manager import CLIManager

def test_cli_commands():
    cli = CLIManager()
    assert cli.run(['bootstrap']) == 0
    assert cli.run(['backfill']) == 0
    assert cli.run(['status']) == 0
    # unknown command
    assert cli.run([]) == 1
