class RoleBasedAccessControl:
    def __init__(self):
        self.user_roles = {}
        self.role_permissions = {}
    def add_role(self, role, permissions):
        self.role_permissions[role] = set(permissions)
    def assign_role(self, user, role):
        self.user_roles[user] = role
    def check_permission(self, user, perm):
        role = self.user_roles.get(user)
        if not role:
            return False
        return perm in self.role_permissions.get(role, set())
