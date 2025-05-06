from .repository import RepositoryManager

class EnvManager:
    def __init__(self):
        # envs maps env_name -> { package_name: version_str, ... }
        self.envs = {}
        self.repo_manager = RepositoryManager()

    def create_env(self, env_name):
        if env_name in self.envs:
            raise ValueError(f"Environment '{env_name}' already exists")
        self.envs[env_name] = {}

    def install_packages(self, env_name, packages):
        """
        Install each package (and its dependencies) into the named environment.
        """
        if env_name not in self.envs:
            raise ValueError(f"Environment '{env_name}' does not exist")
        for pkg in packages:
            self._install(env_name, pkg)

    def _install(self, env_name, pkg):
        # Already installed?
        if pkg in self.envs[env_name]:
            return
        # Search repos for the package
        for repo in self.repo_manager.list_repos():
            if pkg in repo:
                versions = repo[pkg]
                # pick the latest version (lexicographically)
                selected_version = sorted(versions.keys())[-1]
                # record install
                self.envs[env_name][pkg] = selected_version
                # install dependencies
                for dep in versions[selected_version]:
                    self._install(env_name, dep)
                return
        # not found in any repo
        raise KeyError(pkg)

    def package_exists(self, env_name, pkg):
        """
        Return True if pkg is installed in env_name.
        """
        return env_name in self.envs and pkg in self.envs[env_name]

    def get_lockfile(self, env_name):
        """
        Return a lockfile string (one 'pkg==version' per line),
        sorted by package name.
        """
        if env_name not in self.envs:
            raise ValueError(f"Environment '{env_name}' does not exist")
        lines = []
        for pkg in sorted(self.envs[env_name].keys()):
            ver = self.envs[env_name][pkg]
            lines.append(f"{pkg}=={ver}")
        return "\n".join(lines)
