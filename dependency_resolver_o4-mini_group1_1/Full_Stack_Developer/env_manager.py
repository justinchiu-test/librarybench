import os
import time
from utils import (
    ensure_dir, read_json, write_json, copy_file,
    list_dirs, read_text, write_text, get_timestamp_ns
)

class EnvironmentManager:
    def __init__(self, base_dir=None, vuln_db_path=None):
        self.base_dir = base_dir or os.getcwd()
        self.envs_dir = os.path.join(self.base_dir, ".envs")
        self.current_env_file = os.path.join(self.base_dir, ".current_env")
        self.vuln_db_path = vuln_db_path or os.path.join(self.base_dir, "vulnerabilities.json")

        ensure_dir(self.envs_dir)
        if not os.path.exists(self.vuln_db_path):
            write_json(self.vuln_db_path, [])

    def create_env(self, name):
        env = os.path.join(self.envs_dir, name)
        if os.path.exists(env):
            raise ValueError(f"Environment {name} already exists")
        ensure_dir(env)
        write_json(os.path.join(env, "env.json"), {"packages": {}})
        ensure_dir(os.path.join(env, "snapshots"))
        return True

    def delete_env(self, name):
        env = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env):
            raise ValueError(f"Environment {name} does not exist")
        shutil.rmtree(env)
        if self.get_current_env() == name and os.path.exists(self.current_env_file):
            os.remove(self.current_env_file)
        return True

    def list_envs(self):
        return list_dirs(self.envs_dir)

    def switch_env(self, name):
        env = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env):
            raise ValueError(f"Environment {name} does not exist")
        write_text(self.current_env_file, name)
        return True

    def get_current_env(self):
        if not os.path.exists(self.current_env_file):
            return None
        return read_text(self.current_env_file).strip()

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
        ts = get_timestamp_ns()
        snap_dir = self._snapshot_dir(name)
        ensure_dir(snap_dir)
        dst = os.path.join(snap_dir, f"{ts}.json")
        copy_file(src, dst)
        return ts

    def rollback(self, name, timestamp=None):
        snap_dir = self._snapshot_dir(name)
        if not os.path.isdir(snap_dir):
            raise ValueError(f"No snapshots for {name}")
        snaps = sorted(os.listdir(snap_dir))
        if not snaps:
            raise ValueError(f"No snapshots for {name}")
        fname = f"{timestamp}.json" if timestamp else snaps[-1]
        if fname not in snaps:
            raise ValueError(f"Snapshot {timestamp} not found")
        copy_file(os.path.join(snap_dir, fname), self._env_file(name))
        return True

    def _load_env(self, name):
        return read_json(self._env_file(name))

    def _write_env(self, path, data):
        write_json(path, data)

    def install_package(self, pkg_name, version, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        path = self._env_file(name)
        data = self._load_env(name)
        data["packages"][pkg_name] = version
        self._write_env(path, data)
        self.snapshot(name)
        return True

    def remove_package(self, pkg_name, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        path = self._env_file(name)
        data = self._load_env(name)
        if pkg_name not in data["packages"]:
            raise ValueError(f"Package {pkg_name} not installed")
        del data["packages"][pkg_name]
        self._write_env(path, data)
        self.snapshot(name)
        return True

    def generate_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        data = self._load_env(name)
        write_json(self._lock_file(name), data)
        return True

    def install_from_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        lock = self._lock_file(name)
        if not os.path.exists(lock):
            raise ValueError("Lockfile does not exist")
        copy_file(lock, self._env_file(name))
        self.snapshot(name)
        return True

    def alert_vulnerabilities(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        data = self._load_env(name)
        vulns = read_json(self.vuln_db_path)
        return [
            v for pkg, ver in data["packages"].items()
            for v in vulns
            if v.get("name")==pkg and v.get("version")==ver
        ]
