"""Help formatting for backend developer CLI tools."""

from src.cli_core.help_formatter import ColoredHelpFormatter

def format_help(commands, style="plain"):
    """Format commands help text in the specified style."""
    if style == "plain":
        return format_plain(commands)
    elif style == "markdown":
        return format_markdown(commands)
    elif style == "ansi":
        return format_ansi(commands)
    else:
        return format_plain(commands)

def format_plain(commands):
    """Format commands in plain text."""
    lines = []
    for name, desc in commands.items():
        lines.append(f"{name}: {desc}")
    return "\n".join(lines)

def format_markdown(commands):
    """Format commands in markdown."""
    lines = []
    for name, desc in commands.items():
        lines.append(f"### {name}")
        lines.append(f"{desc}")
        lines.append("")
    return "\n".join(lines)

def format_ansi(commands):
    """Format commands with ANSI color codes."""
    lines = []
    for name, desc in commands.items():
        lines.append(f"\033[1m{name}\033[0m: {desc}")
    return "\n".join(lines)