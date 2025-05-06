import os
import shutil
from threading import Lock
from utils import ensure_dir, ensure_file, load_json, write_json

DEFAULT_VULNERABILITY_DB = {
    "openssl": ["1.0.0", "2.0.0"],
    "libssl": ["1.0.0"],
}

class EnvironmentError(Exception):
    pass

class Environment:
    def __init__(self, name, root_path):
        self.name = name
        self.root = os.path.join(root_path, name)
        self.packages_file = os.path.join(self.root, "packages.json")
        self.history_file = os.path.join(self.root, "history.json")
        self.pins_file = os.path.join(self.root, "pins.json")
        self.lockfile = os.path.join(self.root, "lockfile.json")
        self._lock = Lock()
        ensure_dir(self.root)
        ensure_file(self.packages_file, {})
        ensure_file(self.history_file, [])
        ensure_file(self.pins_file, {})

    def _save_all(self):
        write_json(self.packages_file, self.packages)
        write_json(self.history_file, self.history)
        write_json(self.pins_file, self.pins)

    def install_package(self, pkg_name, version=None):
        with self._lock:
            if version is None:
                if pkg_name not in self.pins:
                    raise EnvironmentError(f"Version required for package {pkg_name}")
                version = self.pins[pkg_name]
            self.packages[pkg_name] = version
            self.history.append(dict(self.packages))
            self._save_all()

    def remove_package(self, pkg_name):
        with self._lock:
            if pkg_name not in self.packages:
                raise EnvironmentError(f"Package {pkg_name} not installed")
            del self.packages[pkg_name]
            self.history.append(dict(self.packages))
            self._save_all()

    def generate_lockfile(self):
        data = {"environment": self.name, "packages": dict(self.packages)}
        write_json(self.lockfile, data)
        return self.lockfile

    def install_from_lockfile(self, lockfile_path):
        data = load_json(lockfile_path)
        if "packages" not in data:
            raise EnvironmentError("Invalid lockfile")
        with self._lock:
            self.packages = dict(data["packages"])
            self.history.append(dict(self.packages))
            write_json(self.packages_file, self.packages)

    def check_vulnerabilities(self, vuln_db=None):
        db = vuln_db or DEFAULT_VULNERABILITY_DB
        return [
            {"package": pkg, "version": ver}
            for pkg, ver in self.packages.items()
            if pkg in db and ver in db[pkg]
        ]

    def rollback(self):
        with self._lock:
            if len(self.history) < 2:
                raise EnvironmentError("No previous state to rollback to")
            self.history.pop()
            self.packages = dict(self.history[-1])
            write_json(self.history_file, self.history)
            write_json(self.packages_file, self.packages)

    def pin_version(self, pkg_name, version):
        with self._lock:
            self.pins[pkg_name] = version
            write_json(self.pins_file, self.pins)

    def list_packages(self):
        return dict(self.packages)

class PackageManager:
    def __init__(self, root_path):
        self.root = root_path
        ensure_dir(self.root)
        self.envs = {}
        self.current = None
        self._lock = Lock()

    def create_environment(self, name):
        with self._lock:
            path = os.path.join(self.root, name)
            if name in self.envs or os.path.exists(path):
                raise EnvironmentError(f"Environment {name} already exists")
            env = Environment(name, self.root)
            self.envs[name] = env
            return env

    def delete_environment(self, name):
        with self._lock:
            self.envs.pop(name, None)
            path = os.path.join(self.root, name)
            if os.path.exists(path):
                shutil.rmtree(path)
            else:
                raise EnvironmentError(f"Environment {name} does not exist")

    def list_environments(self):
        return [
            d for d in os.listdir(self.root)
            if os.path.isdir(os.path.join(self.root, d))
        ]

    def switch_environment(self, name):
        with self._lock:
            if name in self.envs:
                self.current = self.envs[name]
            else:
                path = os.path.join(self.root, name)
                if not os.path.exists(path):
                    raise EnvironmentError(f"Environment {name} does not exist")
                self.current = Environment(name, self.root)
                self.envs[name] = self.current
            return self.current

    def get_current_environment(self):
        if not self.current:
            raise EnvironmentError("No environment selected")
        return self.current
