from microcli.commands import register_subcommands

def test_register():
    subs = register_subcommands()
    assert "migrate" in subs
    assert "seed" in subs
    assert "status" in subs
