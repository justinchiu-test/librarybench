import os
import json
from utils import match_constraint

class ConflictError(Exception):
    """Raised when dependencies cannot be resolved."""
    pass

class DependencySolver:
    def __init__(self, repo_urls, offline=False):
        """
        repo_urls: list of file paths or file:// URLs pointing to JSON indexes.
        offline: if True, ignore non-local repositories.
        """
        self.repo_urls = repo_urls
        self.offline = offline
        self.index = {}  # pkg_name -> set of versions

    def load_indexes(self):
        """Load and merge package version indexes from all repositories."""
        for url in self.repo_urls:
            # Determine local file path
            if url.startswith("file://"):
                path = url[7:]
            else:
                path = url
            # In offline mode skip non-local/nonexistent
            if self.offline and not os.path.exists(path):
                continue
            if not os.path.exists(path):
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
                for pkg, versions in data.items():
                    self.index.setdefault(pkg, set()).update(versions)
            except Exception:
                continue
        # Convert to sorted lists
        for pkg in self.index:
            self.index[pkg] = sorted(
                self.index[pkg],
                key=lambda v: tuple(int(x) for x in v.split("."))
            )

    def solve(self, constraints):
        """
        constraints: dict pkg_name -> constraint string
        Returns dict pkg_name -> selected_version
        """
        self.load_indexes()
        result = {}
        for pkg, constraint in constraints.items():
            if pkg not in self.index:
                raise ConflictError(f"Package '{pkg}' not found in repositories.")
            candidates = [
                v for v in self.index[pkg]
                if match_constraint(v, constraint)
            ]
            if not candidates:
                raise ConflictError(
                    f"No versions for package '{pkg}' match constraint '{constraint}'."
                )
            # pick the latest version
            result[pkg] = candidates[-1]
        return result
