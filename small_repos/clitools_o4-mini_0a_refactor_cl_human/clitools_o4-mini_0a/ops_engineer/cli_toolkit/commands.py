class CLIGroup:
    """
    Group of subcommands.
    """
    def __init__(self, name):
        self.name = name
        self.commands = {}
        self.flags = []

    def register(self, command_name, func):
        self.commands[command_name] = func

    def add_flag(self, flag):
        self.flags.append(flag)

class CLI:
    """
    CLI registry for command groups.
    """
    def __init__(self):
        self.groups = {}

    def register_group(self, name):
        group = CLIGroup(name)
        self.groups[name] = group
        return group

    def register_command(self, group_name, command_name, func):
        if group_name not in self.groups:
            self.register_group(group_name)
        self.groups[group_name].register(command_name, func)
