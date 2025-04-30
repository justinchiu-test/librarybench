class AuthError(Exception):
    """Exception raised for authentication errors."""
    pass

class Auth:
    """
    Simple authentication and authorization class.
    Users can be added with roles, can login to obtain a token,
    and be authorized for actions based on roles.
    """
    def __init__(self):
        self._users = {}    # username -> {'password': ..., 'roles': [...]}
        self._tokens = {}   # token -> username

    def add_user(self, username, password, roles=None):
        """
        Add a new user with a password and list of roles.
        """
        if roles is None:
            roles = []
        self._users[username] = {'password': password, 'roles': roles}

    def login(self, username, password):
        """
        Authenticate a user and return a token if successful.
        Raises AuthError on failure.
        """
        user = self._users.get(username)
        if not user or user['password'] != password:
            raise AuthError("Invalid credentials")
        token = username  # In this simple implementation, token == username
        self._tokens[token] = username
        return token

    def authorize(self, token, action):
        """
        Check if the token is valid and if the user has permission for the action.
        Admins can perform any action. Users with 'user' role can add tasks and run scheduler.
        """
        username = self._tokens.get(token)
        if not username:
            return False
        user = self._users.get(username)
        if not user:
            return False
        roles = user.get('roles', [])
        if 'admin' in roles:
            return True
        if action in ('add_task', 'run_scheduler'):
            return 'user' in roles
        return False
