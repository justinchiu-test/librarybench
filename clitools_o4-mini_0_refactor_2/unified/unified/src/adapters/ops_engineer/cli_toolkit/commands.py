"""
Command and group registration for Operations Engineer CLI.
"""
class CommandGroup:
    def __init__(self, name):
        self.name = name
        self.commands = {}

class CLI:
    def __init__(self):
        self.groups = {}

    def register_group(self, name):
        if name not in self.groups:
            self.groups[name] = CommandGroup(name)
        return self.groups[name]

    def register_command(self, group_name, cmd_name, fn):
        group = self.register_group(group_name)
        group.commands[cmd_name] = fn