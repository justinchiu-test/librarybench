ANSI_BOLD = '\033[1m'
ANSI_RESET = '\033[0m'

def format_help(commands, style='text', branding=''):
    """
    Render help in text, markdown, or ANSI style.
    """
    lines = []
    if branding:
        lines.append(branding)
        lines.append('')
    if style == 'markdown':
        for cmd, desc in commands.items():
            lines.append(f"- **{cmd}**: {desc}")
    elif style == 'ansi':
        for cmd, desc in commands.items():
            lines.append(f"{ANSI_BOLD}{cmd}{ANSI_RESET}: {desc}")
    else:
        for cmd, desc in commands.items():
            lines.append(f"{cmd}: {desc}")
    return "\n".join(lines)
