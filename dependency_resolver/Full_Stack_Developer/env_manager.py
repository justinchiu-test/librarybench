import os
import json
import shutil
import time

class EnvironmentManager:
    def __init__(self, base_dir=None, vuln_db_path=None):
        self.base_dir = base_dir or os.getcwd()
        self.envs_dir = os.path.join(self.base_dir, ".envs")
        self.current_env_file = os.path.join(self.base_dir, ".current_env")
        self.vuln_db_path = vuln_db_path or os.path.join(self.base_dir, "vulnerabilities.json")
        os.makedirs(self.envs_dir, exist_ok=True)
        # Ensure vulnerability DB exists
        if not os.path.exists(self.vuln_db_path):
            with open(self.vuln_db_path, "w") as f:
                json.dump([], f)

    def create_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if os.path.exists(env_dir):
            raise ValueError(f"Environment {name} already exists")
        os.makedirs(env_dir)
        # Initialize empty env.json
        with open(os.path.join(env_dir, "env.json"), "w") as f:
            json.dump({"packages": {}}, f, indent=2)
        # Create snapshots folder
        os.makedirs(os.path.join(env_dir, "snapshots"))
        return True

    def delete_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env_dir):
            raise ValueError(f"Environment {name} does not exist")
        shutil.rmtree(env_dir)
        # If it was the current env, remove the pointer
        if self.get_current_env() == name and os.path.exists(self.current_env_file):
            os.remove(self.current_env_file)
        return True

    def list_envs(self):
        return sorted([
            d for d in os.listdir(self.envs_dir)
            if os.path.isdir(os.path.join(self.envs_dir, d))
        ])

    def switch_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env_dir):
            raise ValueError(f"Environment {name} does not exist")
        with open(self.current_env_file, "w") as f:
            f.write(name)
        return True

    def get_current_env(self):
        if not os.path.exists(self.current_env_file):
            return None
        with open(self.current_env_file) as f:
            return f.read().strip()

    def _env_file(self, name):
        return os.path.join(self.envs_dir, name, "env.json")

    def _lock_file(self, name):
        return os.path.join(self.envs_dir, name, "lockfile.json")

    def _snapshot_dir(self, name):
        return os.path.join(self.envs_dir, name, "snapshots")

    def snapshot(self, name):
        src = self._env_file(name)
        if not os.path.exists(src):
            raise ValueError(f"No env.json for {name}")
        # Use high-resolution timestamp so rapid snapshots don't collide
        ts = str(time.time_ns())
        snap_dir = self._snapshot_dir(name)
        os.makedirs(snap_dir, exist_ok=True)
        dst = os.path.join(snap_dir, f"{ts}.json")
        shutil.copy2(src, dst)
        return ts

    def rollback(self, name, timestamp=None):
        snap_dir = self._snapshot_dir(name)
        if not os.path.isdir(snap_dir):
            raise ValueError(f"No snapshots for {name}")
        snaps = sorted(os.listdir(snap_dir))
        if not snaps:
            raise ValueError(f"No snapshots for {name}")
        if timestamp:
            fname = f"{timestamp}.json"
            if fname not in snaps:
                raise ValueError(f"Snapshot {timestamp} not found")
        else:
            fname = snaps[-1]
        shutil.copy2(os.path.join(snap_dir, fname), self._env_file(name))
        return True

    def _load_env(self, name):
        fpath = self._env_file(name)
        with open(fpath) as f:
            return json.load(f)

    def _write_env(self, fpath, data):
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2)

    def install_package(self, pkg_name, version, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        # Load current state
        env_path = self._env_file(name)
        data = self._load_env(name)
        # Apply change
        data["packages"][pkg_name] = version
        self._write_env(env_path, data)
        # Snapshot after change
        self.snapshot(name)
        return True

    def remove_package(self, pkg_name, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        # Load current state
        env_path = self._env_file(name)
        data = self._load_env(name)
        if pkg_name not in data["packages"]:
            raise ValueError(f"Package {pkg_name} not installed")
        # Apply change
        del data["packages"][pkg_name]
        self._write_env(env_path, data)
        # Snapshot after change
        self.snapshot(name)
        return True

    def generate_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        data = self._load_env(name)
        with open(self._lock_file(name), "w") as f:
            json.dump(data, f, indent=2)
        return True

    def install_from_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        lock = self._lock_file(name)
        if not os.path.exists(lock):
            raise ValueError("Lockfile does not exist")
        # Apply lockfile
        shutil.copy2(lock, self._env_file(name))
        # Snapshot after change
        self.snapshot(name)
        return True

    def alert_vulnerabilities(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        data = self._load_env(name)
        with open(self.vuln_db_path) as f:
            vulns = json.load(f)
        alerts = []
        for pkg, ver in data["packages"].items():
            for v in vulns:
                if v.get("name") == pkg and v.get("version") == ver:
                    alerts.append(v)
        return alerts
