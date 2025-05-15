class CommandGroup:
    """A group of related commands"""
    
    def __init__(self, name):
        self.name = name
        self.commands = {}
    
    def add_command(self, name, func):
        """Add a command to this group"""
        self.commands[name] = func
        
    def run_command(self, name, *args, **kwargs):
        """Run a command by name"""
        if name not in self.commands:
            raise ValueError(f"Command '{name}' not found in group '{self.name}'")
        return self.commands[name](*args, **kwargs)


class CLI:
    """Main CLI entry point for handling command groups and commands"""
    
    def __init__(self):
        self.groups = {}
        
    def register_group(self, name):
        """Register a new command group"""
        group = CommandGroup(name)
        self.groups[name] = group
        return group
        
    def register_command(self, group_name, command_name, func):
        """Register a command in a specific group"""
        if group_name not in self.groups:
            raise ValueError(f"Group '{group_name}' not found")
        self.groups[group_name].add_command(command_name, func)
        
    def run(self, group_name, command_name, *args, **kwargs):
        """Run a specific command from a group"""
        if group_name not in self.groups:
            raise ValueError(f"Group '{group_name}' not found")
        return self.groups[group_name].run_command(command_name, *args, **kwargs)