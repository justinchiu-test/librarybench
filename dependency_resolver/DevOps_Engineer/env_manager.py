import json
import os
from collections import defaultdict
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, vstr):
        self.vstr = vstr
        self.parts = tuple(int(p) for p in vstr.split('.'))

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts

    def __str__(self):
        return self.vstr

    def __repr__(self):
        return f"Version('{self.vstr}')"


class PackageSource:
    """
    Represents available packages and their metadata.
    store: dict of pkg_name -> dict of version_str -> {'requires':{pkg:constraint}, 'vulns': [vuln_str,...]}
    """
    def __init__(self, store):
        self.store = {}
        for pkg, versions in store.items():
            self.store[pkg] = {}
            for vstr, meta in versions.items():
                requires = meta.get('requires', {})
                vulns = meta.get('vulns', [])
                self.store[pkg][vstr] = {
                    'requires': requires.copy(),
                    'vulns': list(vulns)
                }

    def available_versions(self, pkg):
        if pkg not in self.store:
            return []
        return sorted((Version(v) for v in self.store[pkg].keys()), reverse=False)

    def latest_version(self, pkg):
        vers = self.available_versions(pkg)
        return vers[-1] if vers else None

    def get_metadata(self, pkg, version):
        ver_str = str(version)
        if pkg not in self.store or ver_str not in self.store[pkg]:
            raise KeyError(f"Package {pkg} version {ver_str} not found in source")
        return self.store[pkg][ver_str]

    def has_package(self, pkg, version=None):
        if pkg not in self.store:
            return False
        if version is None:
            return True
        return str(version) in self.store[pkg]


class EnvironmentManager:
    """
    Manages an isolated environment of installed packages.
    """
    CONFIG_FILE = 'env_config.json'

    def __init__(self, source: PackageSource, env_path=None):
        self.source = source
        self.installed = {}  # pkg_name -> Version
        self.deps = defaultdict(list)  # pkg_name -> list of (dep_pkg, dep_version)
        self.env_path = env_path
        if env_path:
            os.makedirs(env_path, exist_ok=True)
            self.config_path = os.path.join(env_path, self.CONFIG_FILE)
            if os.path.isfile(self.config_path):
                self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        self.installed = {pkg: Version(ver) for pkg, ver in data.get('installed', {}).items()}
        self.deps = defaultdict(list)
        for pkg, edges in data.get('deps', {}).items():
            for dep_pkg, dep_ver in edges:
                self.deps[pkg].append((dep_pkg, Version(dep_ver)))

    def _save_config(self):
        data = {
            'installed': {pkg: str(ver) for pkg, ver in self.installed.items()},
            'deps': {pkg: [(d, str(v)) for d, v in deps] for pkg, deps in self.deps.items()}
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_env(self):
        if not self.env_path:
            raise RuntimeError("No env_path specified")
        self._save_config()

    def install(self, pkg, version=None, offline=False):
        """
        Install pkg into the environment. If version is None, pick latest.
        If offline=True, only source is used (internet not allowed).
        """
        if version is None:
            ver = self.source.latest_version(pkg)
            if ver is None:
                raise KeyError(f"No versions available for package {pkg}")
        else:
            ver = Version(str(version))
            if not self.source.has_package(pkg, ver):
                raise KeyError(f"Package {pkg} version {ver} not found")
        # Install dependencies first
        meta = self.source.get_metadata(pkg, ver)
        for dep, constraint in meta['requires'].items():
            dep_ver = self._select_version(dep, constraint)
            # recursive install
            if dep not in self.installed or self.installed[dep] != dep_ver:
                self.install(dep, dep_ver, offline=offline)
            # record dep
            self.deps[pkg].append((dep, dep_ver))
        # install pkg itself
        self.installed[pkg] = ver
        # save config if env_path
        if self.env_path:
            self._save_config()

    def _select_version(self, pkg, constraint):
        """
        constraint: string like '>=1.0', '==2.0', '<=1.5'
        If constraint is empty, pick latest.
        """
        if not constraint:
            latest = self.source.latest_version(pkg)
            if not latest:
                raise KeyError(f"No versions for {pkg}")
            return latest
        ops = ['>=', '<=', '==', '>', '<']
        for op in ops:
            if constraint.startswith(op):
                ver_str = constraint[len(op):]
                target = Version(ver_str)
                candidates = self.source.available_versions(pkg)
                valid = []
                for v in candidates:
                    if op == '>=' and v >= target:
                        valid.append(v)
                    if op == '<=' and v <= target:
                        valid.append(v)
                    if op == '==' and v == target:
                        valid.append(v)
                    if op == '>' and v > target:
                        valid.append(v)
                    if op == '<' and v < target:
                        valid.append(v)
                if not valid:
                    raise KeyError(f"No version of {pkg} matches constraint {constraint}")
                return max(valid)
        # no operator
        return self.source.latest_version(pkg)

    def package_exists(self, pkg):
        return pkg in self.installed

    def generate_lockfile(self, lockfile_path):
        data = {
            'packages': {pkg: str(ver) for pkg, ver in self.installed.items()}
        }
        with open(lockfile_path, 'w') as f:
            json.dump(data, f, indent=2)

    def notify_updates(self):
        updates = {}
        for pkg, ver in self.installed.items():
            latest = self.source.latest_version(pkg)
            if latest and latest > ver:
                updates[pkg] = {'current': str(ver), 'latest': str(latest)}
        return updates

    def export_env(self, export_path):
        data = {
            'installed': {pkg: str(ver) for pkg, ver in self.installed.items()},
            'deps': {pkg: [(d, str(v)) for d, v in deps] for pkg, deps in self.deps.items()}
        }
        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2)

    def import_env(self, import_path):
        with open(import_path, 'r') as f:
            data = json.load(f)
        self.installed.clear()
        self.deps.clear()
        for pkg, ver in data.get('installed', {}).items():
            self.installed[pkg] = Version(ver)
        for pkg, deps in data.get('deps', {}).items():
            for dep_pkg, dep_ver in deps:
                self.deps[pkg].append((dep_pkg, Version(dep_ver)))
        if self.env_path:
            self._save_config()

    def explain(self, pkg):
        """
        Explain dependencies for pkg: returns list of chains,
        each chain is a list starting from pkg down to a leaf dependency.
        """
        if pkg not in self.installed:
            raise KeyError(f"{pkg} not installed")
        chains = []

        def dfs(current, path):
            if current not in self.deps or not self.deps[current]:
                chains.append(path.copy())
                return
            for dep, _ in self.deps[current]:
                path.append(dep)
                dfs(dep, path)
                path.pop()

        dfs(pkg, [pkg])
        return chains

    def security_alerts(self):
        alerts = {}
        for pkg, ver in self.installed.items():
            meta = self.source.get_metadata(pkg, ver)
            if meta.get('vulns'):
                alerts[pkg] = list(meta['vulns'])
        return alerts

    def solve_and_install(self, constraints, offline=False):
        """
        constraints: list of strings like 'A>=1.0'
        Installs all satisfying latest compatible versions and their deps.
        """
        to_install = {}
        for c in constraints:
            # split pkg and constraint
            for op in ['>=', '<=', '==', '>', '<']:
                if op in c:
                    pkg, rest = c.split(op, 1)
                    pkg = pkg.strip()
                    constr = op + rest.strip()
                    ver = self._select_version(pkg, constr)
                    to_install[pkg] = ver
                    break
            else:
                # no operator, take latest
                pkg = c.strip()
                ver = self.source.latest_version(pkg)
                if not ver:
                    raise KeyError(f"No versions for {pkg}")
                to_install[pkg] = ver
        for pkg, ver in to_install.items():
            self.install(pkg, ver, offline=offline)
