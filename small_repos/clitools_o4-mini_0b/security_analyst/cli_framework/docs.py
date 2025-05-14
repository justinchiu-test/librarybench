def generate_docs(commands):
    """
    commands: dict of command name to description
    """
    lines = ["NAME", "    Secure CLI", "", "SYNOPSIS", "    seccli [COMMAND]", "", "COMMANDS"]
    for cmd, desc in commands.items():
        lines.append(f"    {cmd}\t{desc}")
    lines.append("")
    lines.append("SECURITY")
    lines.append("    All commands enforce signal handling, input validation, and encrypted secrets.")
    return "\n".join(lines)
