import json
import os
from .utils import compare_versions

class RepositoryManager:
    def __init__(self, repo_paths=None):
        self.repos = []
        # load default repo
        default = os.path.join(os.path.dirname(__file__), 'default_repo.json')
        self.add_repo(default)
        if repo_paths:
            for p in repo_paths:
                self.add_repo(p)

    def add_repo(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Repository file not found: {path}")
        with open(path, 'r') as f:
            data = json.load(f)
        self.repos.append({'path': path, 'data': data})

    def remove_repo(self, path):
        self.repos = [r for r in self.repos if r['path'] != path]

    def list_repos(self):
        return [r['path'] for r in self.repos]

    def get_package_info(self, pkg_name):
        # search repos in reverse (last added has priority)
        for repo in reversed(self.repos):
            data = repo['data']
            if pkg_name in data:
                return data[pkg_name]
        raise KeyError(f"Package {pkg_name} not found in any repo")

    def get_available_versions(self, pkg_name):
        info = self.get_package_info(pkg_name)
        return list(info.keys())

    def get_latest_version(self, pkg_name):
        versions = self.get_available_versions(pkg_name)
        # pick max by compare_versions
        latest = versions[0]
        for v in versions[1:]:
            if compare_versions(v, latest) > 0:
                latest = v
        return latest

    def get_dependencies(self, pkg_name, version):
        info = self.get_package_info(pkg_name)
        if version not in info:
            raise KeyError(f"Version {version} of {pkg_name} not found")
        return info[version]
