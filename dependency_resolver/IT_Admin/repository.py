import os
import json

class RepositoryManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.environ.get(
            "ENV_MANAGER_HOME",
            os.path.expanduser("~/.envmanager")
        )
        os.makedirs(self.base_dir, exist_ok=True)
        self.repos_file = os.path.join(self.base_dir, "repos.json")
        if not os.path.exists(self.repos_file):
            with open(self.repos_file, "w") as f:
                json.dump({}, f)
        self._load()

    def _load(self):
        with open(self.repos_file) as f:
            self.repos = json.load(f)

    def _save(self):
        with open(self.repos_file, "w") as f:
            json.dump(self.repos, f, indent=2)

    def add_repository(self, name, url):
        """Add a custom repository by name and URL/path."""
        if name in self.repos:
            raise KeyError(f"Repository '{name}' already exists.")
        self.repos[name] = url
        self._save()

    def remove_repository(self, name):
        """Remove a named repository."""
        if name not in self.repos:
            raise KeyError(f"Repository '{name}' does not exist.")
        del self.repos[name]
        self._save()

    def list_repositories(self):
        """Return a dict of repository name -> URL."""
        return dict(self.repos)

    def get_repository_urls(self):
        """Return list of repository URLs/paths."""
        return list(self.repos.values())
