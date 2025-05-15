def format_help(commands, fmt="plain"):
    """
    Format command help in different formats
    
    Args:
        commands: Dictionary of command names to descriptions
        fmt: Format to use ('plain', 'markdown', 'ansi')
        
    Returns:
        str: Formatted help text
    """
    if fmt == "plain":
        # Simple plain text format
        lines = [f"{cmd}: {desc}" for cmd, desc in commands.items()]
        return "\n".join(lines)
    
    elif fmt == "markdown":
        # Markdown format
        lines = [
            "# Commands",
            ""
        ]
        
        for cmd, desc in commands.items():
            lines.append(f"### {cmd}")
            lines.append(f"{desc}")
            lines.append("")
            
        return "\n".join(lines)
    
    elif fmt == "ansi":
        # ANSI color format
        lines = []
        
        for cmd, desc in commands.items():
            lines.append(f"\033[1m{cmd}\033[0m: {desc}")
            
        return "\n".join(lines)
    
    else:
        raise ValueError(f"Unknown format: {fmt}")