import os
import shutil
from utils import (
    ensure_dir, ensure_file, load_json, write_json,
    remove_file, list_dirs, copy_file, time_ns
)

class EnvironmentManager:
    def __init__(self, base_dir=None, vuln_db_path=None):
        self.base_dir = base_dir or os.getcwd()
        self.envs_dir = os.path.join(self.base_dir, ".envs")
        self.current_env_file = os.path.join(self.base_dir, ".current_env")
        self.vuln_db_path = vuln_db_path or os.path.join(self.base_dir, "vulnerabilities.json")
        ensure_dir(self.envs_dir)
        ensure_file(self.vuln_db_path, [])

    def create_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if os.path.exists(env_dir):
            raise ValueError(f"Environment {name} already exists")
        ensure_dir(env_dir)
        write_json(os.path.join(env_dir, "env.json"), {"packages": {}})
        ensure_dir(self._snapshot_dir(name))
        return True

    def delete_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env_dir):
            raise ValueError(f"Environment {name} does not exist")
        shutil.rmtree(env_dir)
        if self.get_current_env() == name:
            remove_file(self.current_env_file)
        return True

    def list_envs(self):
        return sorted(list_dirs(self.envs_dir))

    def switch_env(self, name):
        env_dir = os.path.join(self.envs_dir, name)
        if not os.path.isdir(env_dir):
            raise ValueError(f"Environment {name} does not exist")
        # write plain text for current env
        with open(self.current_env_file, 'w') as f:
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
        ts = str(time_ns())
        dst = os.path.join(self._snapshot_dir(name), f"{ts}.json")
        ensure_dir(self._snapshot_dir(name))
        copy_file(src, dst)
        return ts

    def rollback(self, name, timestamp=None):
        sd = self._snapshot_dir(name)
        if not os.path.isdir(sd):
            raise ValueError(f"No snapshots for {name}")
        snaps = sorted(os.listdir(sd))
        if not snaps:
            raise ValueError(f"No snapshots for {name}")
        fname = f"{timestamp}.json" if timestamp else snaps[-1]
        if timestamp and fname not in snaps:
            raise ValueError(f"Snapshot {timestamp} not found")
        copy_file(os.path.join(sd, fname), self._env_file(name))
        return True

    def _load_env(self, name):
        return load_json(self._env_file(name))

    def _write_env(self, path, data):
        write_json(path, data)

    def install_package(self, pkg_name, version, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        fp = self._env_file(name)
        data = self._load_env(name)
        data["packages"][pkg_name] = version
        self._write_env(fp, data)
        self.snapshot(name)
        return True

    def remove_package(self, pkg_name, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        fp = self._env_file(name)
        data = self._load_env(name)
        if pkg_name not in data["packages"]:
            raise ValueError(f"Package {pkg_name} not installed")
        data["packages"].pop(pkg_name)
        self._write_env(fp, data)
        self.snapshot(name)
        return True

    def generate_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        write_json(self._lock_file(name), self._load_env(name))
        return True

    def install_from_lockfile(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        lf = self._lock_file(name)
        if not os.path.exists(lf):
            raise ValueError("Lockfile does not exist")
        copy_file(lf, self._env_file(name))
        self.snapshot(name)
        return True

    def alert_vulnerabilities(self, env=None):
        name = env or self.get_current_env()
        if not name:
            raise ValueError("No environment selected")
        data = self._load_env(name)
        vulns = load_json(self.vuln_db_path)
        return [v for v in vulns
                if data["packages"].get(v.get("name")) == v.get("version")]
