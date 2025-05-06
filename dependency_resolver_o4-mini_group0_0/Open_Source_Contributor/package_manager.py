import os
import json
from utils import compare_versions, parse_spec_multi, satisfies_constraints, parse_version

# load indexes once
_THIS_DIR = os.path.dirname(__file__)
with open(os.path.join(_THIS_DIR, "package_index.json"), 'r', encoding='utf-8') as f:
    PACKAGE_INDEX = json.load(f)
with open(os.path.join(_THIS_DIR, "local_index.json"), 'r', encoding='utf-8') as f:
    LOCAL_INDEX = json.load(f)

class Environment:
    def __init__(self, path):
        self.path = path
        self.installed_file = os.path.join(path, "installed.json")
        self.reasons = {}
        if os.path.exists(self.installed_file):
            with open(self.installed_file, 'r', encoding='utf-8') as f:
                self.installed = json.load(f)
        else:
            self.installed = {}

    @classmethod
    def create_env(cls, path):
        os.makedirs(path, exist_ok=True)
        instf = os.path.join(path, "installed.json")
        if not os.path.exists(instf):
            with open(instf, "w", encoding='utf-8') as f:
                json.dump({}, f)
        return cls(path)

    def save(self):
        with open(self.installed_file, "w", encoding='utf-8') as f:
            json.dump(self.installed, f, indent=2)

    def is_installed(self, name):
        return name in self.installed

    def install(self, spec, offline=False, parent=None):
        name, constraints = parse_spec_multi(spec)
        index = LOCAL_INDEX if offline else (PACKAGE_INDEX if name in PACKAGE_INDEX else LOCAL_INDEX)
        if name not in index:
            raise ValueError(f"Package {name} not found in {'local' if offline else 'remote'} index")
        versions = list(index[name].keys())
        candidates = [v for v in versions if satisfies_constraints(v, constraints)]
        if not candidates:
            raise ValueError(f"No available version for {name} matching {constraints}")
        candidates.sort(key=lambda v: parse_version(v))
        version = candidates[-1]
        if self.installed.get(name) == version:
            return
        self.reasons[name] = parent or "user"
        for dep in index[name][version].get("dependencies", []):
            self.install(dep, offline=offline, parent=name)
        self.installed[name] = version
        self.save()

    def freeze(self, lockfile_path):
        with open(lockfile_path, 'w', encoding='utf-8') as f:
            json.dump(self.installed, f, indent=2)

    def export_env(self, export_path):
        self.freeze(export_path)

    def import_env(self, lockfile_path):
        if not os.path.exists(lockfile_path):
            raise ValueError(f"Lockfile {lockfile_path} not found")
        with open(lockfile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.installed = data.copy()
        for pkg in self.installed:
            self.reasons[pkg] = "user"
        self.save()

    def list_updates(self):
        updates = {}
        for name, curver in self.installed.items():
            if name in PACKAGE_INDEX:
                allv = list(PACKAGE_INDEX[name].keys())
                allv.sort(key=lambda v: parse_version(v))
                latest = allv[-1]
                if compare_versions(latest, curver) > 0:
                    updates[name] = (curver, latest)
        return updates

    def check_vulnerabilities(self):
        vulns = {}
        for name, ver in self.installed.items():
            src = PACKAGE_INDEX if name in PACKAGE_INDEX else LOCAL_INDEX
            vs = src[name][ver].get("vulnerabilities", []) if name in src and ver in src[name] else []
            if vs:
                vulns[name] = vs.copy()
        return vulns

    def explain(self, name):
        if name not in self.installed:
            raise ValueError(f"{name} is not installed")
        chain = []
        cur = name
        while True:
            chain.append(cur)
            reason = self.reasons.get(cur)
            if reason is None or reason == "user":
                chain.append("user")
                break
            cur = reason
        return chain
