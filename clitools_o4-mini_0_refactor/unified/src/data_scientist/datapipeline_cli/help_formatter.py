"""
Help formatter for data scientists.
"""
def format_help(commands, mode='plain'):
    mode = mode.lower()
    if mode == 'md':
        lines = []
        for cmd, desc in commands.items():
            lines.append(f"### `{cmd}`\n\n{desc}")
        return '\n'.join(lines)
    elif mode == 'color':
        lines = []
        for cmd, desc in commands.items():
            lines.append(f"\033[94m{cmd}\033[0m: {desc}")
        return '\n'.join(lines)
    else:
        raise ValueError(f"Unknown mode: {mode}")