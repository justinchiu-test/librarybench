import os
from Software_Developer.utils import load_json, dump_json

class RepositoryManager:
    def __init__(self, config_file="repos.json"):
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            self.repos = load_json(self.config_file)
        else:
            self.repos = {}

    def _save(self):
        dump_json(self.repos, self.config_file)

    def add_repo(self, name, packages):
        if name in self.repos:
            raise ValueError(f"Repo '{name}' already exists")
        if not isinstance(packages, dict):
            raise ValueError("packages must be a dict")
        for vers in packages.values():
            if not isinstance(vers, list):
                raise ValueError("versions must be a list")
        self.repos[name] = packages
        self._save()

    def remove_repo(self, name):
        if name not in self.repos:
            raise KeyError(f"Repo '{name}' does not exist")
        del self.repos[name]
        self._save()

    def list_repos(self):
        return self.repos.copy()

    def get_all_packages(self):
        out = {}
        for pkgs in self.repos.values():
            for pkg, vers in pkgs.items():
                out.setdefault(pkg, set()).update(vers)
        return out
