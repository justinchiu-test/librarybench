"""
Generate simple documentation for security analysts.
"""
def generate_docs(cmds):
    # cmds: dict of command: description
    lines = []
    # header
    lines.append('SECURITY CLI Documentation')
    for cmd, desc in cmds.items():
        lines.append(f"{cmd}\t{desc}")
    return '\n'.join(lines)