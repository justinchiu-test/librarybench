class ConcurrencyControl:
    def __init__(self, max_global=1, max_per_group=None):
        self.max_global = max_global
        self.max_per_group = max_per_group or {}
        self.active_global = 0
        self.active_per_group = {}

    def acquire(self, group):
        if self.active_global >= self.max_global:
            return False
        group_limit = self.max_per_group.get(group)
        if group_limit is not None and self.active_per_group.get(group, 0) >= group_limit:
            return False
        self.active_global += 1
        self.active_per_group[group] = self.active_per_group.get(group, 0) + 1
        return True

    def release(self, group):
        if self.active_per_group.get(group, 0) > 0:
            self.active_per_group[group] -= 1
            self.active_global = max(0, self.active_global - 1)
            return True
        return False
