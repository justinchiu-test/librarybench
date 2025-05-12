"""
Help text formatting for backend developers.
"""
def format_help(commands, fmt='plain'):
    lines = []
    fmt = fmt.lower()
    if fmt == 'plain':
        for cmd, desc in commands.items():
            lines.append(f"{cmd}: {desc}")
    elif fmt == 'markdown':
        for cmd, desc in commands.items():
            lines.append(f"### {cmd}\n{desc}")
    elif fmt == 'ansi':
        for cmd, desc in commands.items():
            lines.append(f"\033[1m{cmd}\033[0m: {desc}")
    else:
        raise ValueError(f"Unknown format: {fmt}")
    return '\n'.join(lines)