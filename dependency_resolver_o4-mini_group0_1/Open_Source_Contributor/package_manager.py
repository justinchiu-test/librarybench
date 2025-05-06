import os
import json
from utils import compare_versions, parse_constraints, satisfies_constraints, parse_version

# load indexes once
_THIS_DIR = os.path.dirname(__file__)
with open(os.path.join(_THIS_DIR, "package_index.json")) as f:
    PACKAGE_INDEX = json.load(f)
with open(os.path.join(_THIS_DIR, "local_index.json")) as f:
    LOCAL_INDEX = json.load(f)

class Environment:
    def __init__(self, path):
        self.path = path
        self.installed_file = os.path.join(path, "installed.json")
        self.reasons = {}
        if os.path.exists(self.installed_file):
            with open(self.installed_file) as f:
                self.installed = json.load(f)
        else:
            self.installed = {}

    @classmethod
    def create_env(cls, path):
        os.makedirs(path, exist_ok=True)
        instf = os.path.join(path, "installed.json")
        if not os.path.exists(instf):
            with open(instf, "w") as f:
                json.dump({}, f)
        return cls(path)

    def save(self):
        with open(self.installed_file, "w") as f:
            json.dump(self.installed, f, indent=2)

    def is_installed(self, name):
        return name in self.installed

    def install(self, spec, offline=False, parent=None):
        name, constraints = parse_constraints(spec)
        # choose index
        if offline:
            index = LOCAL_INDEX
        else:
            index = PACKAGE_INDEX if name in PACKAGE_INDEX else LOCAL_INDEX
        if name not in index:
            src = "local" if offline else "remote"
            raise ValueError(f"Package {name} not found in {src} index")
        versions = list(index[name].keys())
        candidates = [v for v in versions if satisfies_constraints(v, constraints)]
        if not candidates:
            raise ValueError(f"No available version for {name} matching {constraints}")
        candidates.sort(key=parse_version)
        version = candidates[-1]
        # already at version?
        if self.installed.get(name) == version:
            return
        self.reasons[name] = parent or "user"
        # install dependencies
        for dep in index[name][version].get("dependencies", []):
            self.install(dep, offline=offline, parent=name)
        self.installed[name] = version
        self.save()

    def freeze(self, lockfile_path):
        with open(lockfile_path, "w") as f:
            json.dump(self.installed, f, indent=2)

    def export_env(self, export_path):
        self.freeze(export_path)

    def import_env(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        self.installed = data.copy()
        for pkg in self.installed:
            self.reasons[pkg] = "user"
        self.save()

    def list_updates(self):
        updates = {}
        for n, cur in self.installed.items():
            if n in PACKAGE_INDEX:
                allv = sorted(PACKAGE_INDEX[n].keys(), key=parse_version)
                latest = allv[-1]
                if compare_versions(latest, cur) > 0:
                    updates[n] = (cur, latest)
        return updates

    def check_vulnerabilities(self):
        vulns = {}
        for n, ver in self.installed.items():
            if n in PACKAGE_INDEX and ver in PACKAGE_INDEX[n]:
                vs = PACKAGE_INDEX[n][ver].get("vulnerabilities", [])
            elif n in LOCAL_INDEX and ver in LOCAL_INDEX[n]:
                vs = LOCAL_INDEX[n][ver].get("vulnerabilities", [])
            else:
                vs = []
            if vs:
                vulns[n] = vs.copy()
        return vulns

    def explain(self, name):
        if name not in self.installed:
            raise ValueError(f"{name} is not installed")
        chain = []
        cur = name
        while True:
            chain.append(cur)
            reason = self.reasons.get(cur)
            if not reason or reason == "user":
                chain.append("user")
                break
            cur = reason
        return chain
