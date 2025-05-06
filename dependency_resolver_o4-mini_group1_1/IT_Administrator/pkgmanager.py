import os
import json
import shutil
import platform
from threading import Lock

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
        self._ensure_dirs()
        self._load_files()

    def _ensure_dirs(self):
        os.makedirs(self.root, exist_ok=True)

    def _load_files(self):
        # load or init packages
        if os.path.exists(self.packages_file):
            with open(self.packages_file) as f:
                self.packages = json.load(f)
        else:
            self.packages = {}
        # history
        if os.path.exists(self.history_file):
            with open(self.history_file) as f:
                self.history = json.load(f)
        else:
            self.history = []
        # pins
        if os.path.exists(self.pins_file):
            with open(self.pins_file) as f:
                self.pins = json.load(f)
        else:
            self.pins = {}
        # always record initial state if history empty
        if not self.history:
            self._save_history()

    def _save_packages(self):
        with open(self.packages_file, "w") as f:
            json.dump(self.packages, f, indent=2)

    def _save_pins(self):
        with open(self.pins_file, "w") as f:
            json.dump(self.pins, f, indent=2)

    def _save_history(self):
        # snapshot current packages
        snapshot = dict(self.packages)
        self.history.append(snapshot)
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def install_package(self, pkg_name, version=None):
        with self._lock:
            # determine version
            if version is None:
                if pkg_name in self.pins:
                    version = self.pins[pkg_name]
                else:
                    raise EnvironmentError(f"Version required for package {pkg_name}")
            # simulate install
            self.packages[pkg_name] = version
            self._save_packages()
            self._save_history()

    def remove_package(self, pkg_name):
        with self._lock:
            if pkg_name in self.packages:
                del self.packages[pkg_name]
                self._save_packages()
                self._save_history()
            else:
                raise EnvironmentError(f"Package {pkg_name} not installed")

    def generate_lockfile(self):
        data = {
            "environment": self.name,
            "packages": dict(self.packages),
        }
        with open(self.lockfile, "w") as f:
            json.dump(data, f, indent=2)
        return self.lockfile

    def install_from_lockfile(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        if "packages" not in data:
            raise EnvironmentError("Invalid lockfile")
        with self._lock:
            self.packages = dict(data["packages"])
            self._save_packages()
            self._save_history()

    def check_vulnerabilities(self, vuln_db=None):
        if vuln_db is None:
            vuln_db = DEFAULT_VULNERABILITY_DB
        alerts = []
        for pkg, ver in self.packages.items():
            if pkg in vuln_db and ver in vuln_db[pkg]:
                alerts.append({"package": pkg, "version": ver})
        return alerts

    def rollback(self):
        with self._lock:
            if len(self.history) < 2:
                raise EnvironmentError("No previous state to rollback to")
            # drop latest snapshot
            self.history.pop()
            # revert to previous snapshot
            prev = self.history[-1]
            self.packages = dict(prev)
            # persist history without adding a new snapshot
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
            # persist packages
            self._save_packages()

    def pin_version(self, pkg_name, version):
        with self._lock:
            self.pins[pkg_name] = version
            self._save_pins()

    def list_packages(self):
        return dict(self.packages)

class PackageManager:
    def __init__(self, root_path):
        self.root = root_path
        os.makedirs(self.root, exist_ok=True)
        self.envs = {}
        self.current = None
        self._lock = Lock()

    def create_environment(self, name):
        with self._lock:
            if name in self.envs or os.path.exists(os.path.join(self.root, name)):
                raise EnvironmentError(f"Environment {name} already exists")
            env = Environment(name, self.root)
            self.envs[name] = env
            return env

    def delete_environment(self, name):
        with self._lock:
            if name in self.envs:
                # remove from registry
                del self.envs[name]
            path = os.path.join(self.root, name)
            if os.path.exists(path):
                shutil.rmtree(path)
            else:
                raise EnvironmentError(f"Environment {name} does not exist")

    def list_environments(self):
        dirs = [
            name for name in os.listdir(self.root)
            if os.path.isdir(os.path.join(self.root, name))
        ]
        return dirs

    def switch_environment(self, name):
        with self._lock:
            if name not in self.envs:
                # maybe exists on disk
                if os.path.exists(os.path.join(self.root, name)):
                    env = Environment(name, self.root)
                    self.envs[name] = env
                else:
                    raise EnvironmentError(f"Environment {name} does not exist")
            self.current = self.envs[name]
            return self.current

    def get_current_environment(self):
        if self.current is None:
            raise EnvironmentError("No environment selected")
        return self.current
