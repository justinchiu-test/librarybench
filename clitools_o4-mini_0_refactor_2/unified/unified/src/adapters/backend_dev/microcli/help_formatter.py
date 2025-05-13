"""
Help formatter for backend_dev microcli.
Supports plain, markdown, and ANSI formats.
"""
def format_help(commands, mode='plain'):
    if mode == 'plain':
        return '\n'.join(f"{k}: {v}" for k, v in commands.items())
    elif mode == 'markdown':
        # Markdown: headers
        return '\n'.join(f"### {k}\n\n{v}" for k, v in commands.items())
    elif mode == 'ansi':
        bold_start = '\033[1m'
        bold_end = '\033[0m'
        return '\n'.join(f"{bold_start}{k}{bold_end}: {v}" for k, v in commands.items())
    else:
        raise ValueError(f"Unknown format: {mode}")