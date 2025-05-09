import os
import json

class RepositoryManager:
    def __init__(self, config_file="repos.json"):
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            with open(self.config_file) as f:
                self.repos = json.load(f)
        else:
            self.repos = {}
        # repos is dict: name -> dict of pkg -> [versions]

    def _save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.repos, f, indent=2)

    def add_repo(self, name, packages):
        """packages: dict pkg_name -> list of version strings"""
        if name in self.repos:
            raise ValueError(f"Repo '{name}' already exists")
        # validate
        if not isinstance(packages, dict):
            raise ValueError("packages must be a dict")
        for pkg, versions in packages.items():
            if not isinstance(versions, list):
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
        """Return dict pkg_name -> set of versions from all repos"""
        out = {}
        for packages in self.repos.values():
            for pkg, vers in packages.items():
                out.setdefault(pkg, set()).update(vers)
        return out
