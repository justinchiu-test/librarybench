import os
import json

# Path to the built-in default repository
DEFAULT_REPO_PATH = os.path.join(os.path.dirname(__file__), "default_repo.json")

# Module-level store of added repo paths
_additional_repos = []

class RepositoryManager:
    def list_repo_paths(self):
        """
        Return a list of filesystem paths to all repos:
        first the built-in default, then any user-added ones.
        """
        return [DEFAULT_REPO_PATH] + list(_additional_repos)

    def list_repos(self):
        """
        Load and return the JSON contents of each repo as a dict.
        """
        repos = []
        for path in self.list_repo_paths():
            with open(path, "r") as f:
                repos.append(json.load(f))
        return repos

    def add_repo(self, path):
        """
        Add a new repo file path into the in-memory list.
        """
        _additional_repos.append(path)
