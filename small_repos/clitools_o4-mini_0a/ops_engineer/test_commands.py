from cli_toolkit.commands import CLI

def test_register_group_and_command():
    cli = CLI()
    grp = cli.register_group('db')
    assert 'db' in cli.groups
    def dummy(): pass
    cli.register_command('db', 'migrate', dummy)
    assert 'migrate' in cli.groups['db'].commands
