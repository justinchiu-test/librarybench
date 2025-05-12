"""
CLI command registration for ops engineers.
"""
"""
CLI group and command registration for ops engineers.
"""
class Group:
    def __init__(self):
        self.commands = {}

class CLI:
    def __init__(self):
        self.groups = {}

    def register_group(self, name):
        grp = Group()
        self.groups[name] = grp
        return grp

    def register_command(self, group_name, command_name, func):
        if group_name not in self.groups:
            raise KeyError(f"Group not found: {group_name}")
        self.groups[group_name].commands[command_name] = func