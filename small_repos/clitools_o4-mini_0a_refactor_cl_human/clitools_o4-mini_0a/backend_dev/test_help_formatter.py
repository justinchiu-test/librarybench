from microcli.help_formatter import format_help

commands = {"cmd": "does something"}

def test_plain():
    out = format_help(commands, "plain")
    assert "cmd: does something" in out

def test_markdown():
    out = format_help(commands, "markdown")
    assert "### cmd" in out

def test_ansi():
    out = format_help(commands, "ansi")
    assert "\033[1mcmd\033[0m" in out
