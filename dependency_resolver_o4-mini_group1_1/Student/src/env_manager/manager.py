import os
import json
from .repository import RepositoryManager
from .cache import CacheManager

class EnvManager:
    def __init__(self, root=None, repo_manager=None, cache_manager=None):
        self.root = root or os.getenv('ENVMGR_ROOT') or os.path.join(os.getcwd(), '.envs')
        os.makedirs(self.root, exist_ok=True)
        self.repo = repo_manager or RepositoryManager()
        self.cache = cache_manager or CacheManager()

    def _env_path(self, name):
        return os.path.join(self.root, name)

    def create_env(self, name):
        path = self._env_path(name)
        if os.path.exists(path):
            raise FileExistsError(f"Environment {name} already exists")
        os.makedirs(path)
        # installed metadata
        with open(os.path.join(path, 'installed.json'), 'w') as f:
            json.dump({}, f)

    def delete_env(self, name):
        import shutil
        path = self._env_path(name)
        if not os.path.isdir(path):
            raise FileNotFoundError(f"No such environment {name}")
        shutil.rmtree(path)

    def list_envs(self):
        return [d for d in os.listdir(self.root) if os.path.isdir(self._env_path(d))]

    def _load_installed(self, name):
        path = os.path.join(self._env_path(name), 'installed.json')
        with open(path, 'r') as f:
            return json.load(f)

    def _save_installed(self, name, data):
        path = os.path.join(self._env_path(name), 'installed.json')
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def package_exists(self, env, pkg):
        installed = self._load_installed(env)
        return pkg in installed

    def install_packages(self, env, pkgs):
        for p in pkgs:
            self._install_single(env, p)

    def _install_single(self, env, pkg, version=None, seen=None):
        if seen is None: seen = set()
        if pkg in seen:
            return
        seen.add(pkg)
        installed = self._load_installed(env)
        if pkg in installed:
            # already installed
            return
        # pick version
        ver = version or self.repo.get_latest_version(pkg)
        # resolve dependencies first
        deps = self.repo.get_dependencies(pkg, ver)
        for d in deps:
            self._install_single(env, d, None, seen)
        # fetch package (cache)
        self.cache.fetch_package(pkg, ver)
        # record install
        installed[pkg] = {'version': ver, 'dependencies': deps}
        self._save_installed(env, installed)

    def explain_dependency(self, env, pkg):
        installed = self._load_installed(env)
        if pkg not in installed:
            raise KeyError(f"{pkg} not installed in {env}")
        lines = []
        def _recurse(p, depth):
            meta = installed[p]
            lines.append("  " * depth + f"{p}=={meta['version']}")
            for d in meta['dependencies']:
                _recurse(d, depth+1)
        _recurse(pkg, 0)
        return "\n".join(lines)

    def export_lockfile(self, env, filepath):
        installed = self._load_installed(env)
        # only pkg->version
        lock = {p: meta['version'] for p, meta in installed.items()}
        with open(filepath, 'w') as f:
            json.dump({'packages': lock}, f, indent=2)

    def install_from_lockfile(self, env, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        pkgs = data.get('packages', {})
        for p, v in pkgs.items():
            self._install_single(env, p, version=v)

    def import_env(self, env, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        pkgs = data.get('packages', [])
        self.install_packages(env, pkgs)

    def get_update_notifications(self, env):
        installed = self._load_installed(env)
        notifications = {}
        for p, meta in installed.items():
            latest = self.repo.get_latest_version(p)
            if latest != meta['version']:
                notifications[p] = {'current': meta['version'], 'latest': latest}
        return notifications
