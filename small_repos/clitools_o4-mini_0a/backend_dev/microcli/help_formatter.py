def format_help(commands: dict, style: str = "plain") -> str:
    lines = []
    for name, desc in commands.items():
        if style == "markdown":
            lines.append(f"### {name}\n\n{desc}\n")
        elif style == "ansi":
            lines.append(f"\033[1m{name}\033[0m: {desc}")
        else:
            lines.append(f"{name}: {desc}")
    return "\n".join(lines)
