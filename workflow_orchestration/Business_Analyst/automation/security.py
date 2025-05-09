class User:
    def __init__(self, username, roles=None):
        self.username = username
        self.roles = set(roles or [])

class SecurityManager:
    """
    Manages users, authentication, and permission checks.
    """
    def __init__(self):
        self.users = {}
        self.current_user = None

    def add_user(self, username, roles=None):
        """
        Add a new user with given roles.
        """
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")
        self.users[username] = User(username, roles)

    def authenticate(self, username):
        """
        Set current user by username.
        """
        if username not in self.users:
            raise ValueError(f"User '{username}' not found")
        self.current_user = self.users[username]

    def check_permission(self, required_role):
        """
        Check if the current user has the required role.
        Raises PermissionError otherwise.
        """
        if self.current_user is None:
            raise PermissionError("No user authenticated")
        if required_role not in self.current_user.roles:
            raise PermissionError(f"User lacks role: {required_role}")
