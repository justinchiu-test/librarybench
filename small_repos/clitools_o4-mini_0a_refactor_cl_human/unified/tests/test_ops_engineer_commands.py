from src.personas.ops_engineer.cli_toolkit.commands import InfraCommands
from src.core.commands.registry import CommandRegistry

def test_register_infra_commands():
    # Create a command registry
    registry = CommandRegistry("infra")
    
    # Register the infrastructure commands
    commands = InfraCommands(registry)
    
    # Check that the group and its commands were registered
    cmd = registry.find_command("infra:deploy")
    assert cmd is not None
    
    cmd = registry.find_command("infra:status")
    assert cmd is not None
    
    cmd = registry.find_command("infra:validate")
    assert cmd is not None
    
    cmd = registry.find_command("infra:plan")
    assert cmd is not None
    
    # Check the tree structure
    tree = registry.get_command_tree()
    assert "infra" in str(tree)
    assert "deploy" in str(tree)