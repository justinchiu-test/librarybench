from src.core.commands.help import HelpFormatter, FormatStyle
from src.core.commands.registry import Command, CommandRegistry

def test_plain():
    # Create a command registry
    registry = CommandRegistry("test-app")
    
    # Add a command
    registry.add_command("cmd", lambda: None, "does something")
    
    # Create a formatter and format help
    formatter = HelpFormatter(FormatStyle.PLAIN)
    out = formatter.format_command_registry(registry)
    
    # Verify output
    assert "cmd" in out
    assert "does something" in out

def test_markdown():
    # Create a command registry
    registry = CommandRegistry("test-app")
    
    # Add a command
    registry.add_command("cmd", lambda: None, "does something")
    
    # Create a formatter and format help
    formatter = HelpFormatter(FormatStyle.MARKDOWN)
    out = formatter.format_command_registry(registry)
    
    # Verify output contains markdown formatting
    assert "# test-app" in out
    assert "### `cmd`" in out
    assert "does something" in out

def test_ansi():
    # Create a command registry
    registry = CommandRegistry("test-app")
    
    # Add a command
    registry.add_command("cmd", lambda: None, "does something")
    
    # Create a formatter and format help
    formatter = HelpFormatter(FormatStyle.ANSI)
    out = formatter.format_command_registry(registry)
    
    # Verify output contains ANSI formatting (bold)
    assert "\033[1m" in out  # Bold
    assert "cmd" in out
    assert "does something" in out