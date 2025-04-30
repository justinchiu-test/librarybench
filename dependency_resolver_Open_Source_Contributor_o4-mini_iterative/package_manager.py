import os
import json

# load indexes once
_THIS_DIR = os.path.dirname(__file__)
with open(os.path.join(_THIS_DIR, "package_index.json")) as f:
    PACKAGE_INDEX = json.load(f)
with open(os.path.join(_THIS_DIR, "local_index.json")) as f:
    LOCAL_INDEX = json.load(f)

def _compare_versions(v1, v2):
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]
    # pad shorter
    length = max(len(parts1), len(parts2))
    parts1 += [0] * (length - len(parts1))
    parts2 += [0] * (length - len(parts2))
    if parts1 < parts2:
        return -1
    if parts1 > parts2:
        return 1
    return 0

def _satisfies(version, constraints):
    # constraints: list of (op, ver)
    for op, ver in constraints:
        cmp = _compare_versions(version, ver)
        if op == "==" and cmp != 0:
            return False
        if op == ">=" and cmp < 0:
            return False
        if op == "<=" and cmp > 0:
            return False
        if op == ">" and cmp <= 0:
            return False
        if op == "<" and cmp >= 0:
            return False
    return True

def _parse_spec(spec):
    # "name>=1.0,<2.0" or "name"
    name = spec
    raw = ""
    for i, ch in enumerate(spec):
        if ch in "<>=":
            name = spec[:i]
            raw = spec[i:]
            break
    constraints = []
    if raw:
        parts = raw.split(",")
        for part in parts:
            part = part.strip()
            if part.startswith(">="):
                constraints.append((">=", part[2:]))
            elif part.startswith("<="):
                constraints.append(("<=", part[2:]))
            elif part.startswith(">"):
                constraints.append((">", part[1:]))
            elif part.startswith("<"):
                constraints.append(("<", part[1:]))
            elif part.startswith("=="):
                constraints.append(("==", part[2:]))
            else:
                raise ValueError(f"Unknown constraint: {part}")
    # simplify cases like >=v and <v to ==v
    lb_versions = {v for op, v in constraints if op == ">="}
    lt_versions = {v for op, v in constraints if op == "<"}
    common = lb_versions & lt_versions
    if common:
        # remove the >=v and <v for each common v, replace with ==v
        new_cons = []
        for op, v in constraints:
            if v in common and op in (">=", "<"):
                continue
            new_cons.append((op, v))
        for v in common:
            new_cons.append(("==", v))
        constraints = new_cons
    return name, constraints

class Environment:
    def __init__(self, path):
        self.path = path
        self.installed_file = os.path.join(path, "installed.json")
        self.reasons = {}  # package -> parent or 'user'
        if os.path.exists(self.installed_file):
            self.installed = json.load(open(self.installed_file))
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
        name, constraints = _parse_spec(spec)
        # pick index
        if offline:
            index = LOCAL_INDEX
        else:
            # prefer remote, fallback local
            if name in PACKAGE_INDEX:
                index = PACKAGE_INDEX
            else:
                index = LOCAL_INDEX
        if name not in index:
            raise ValueError(f"Package {name} not found in {'local' if offline else 'remote'} index")
        versions = list(index[name].keys())
        # filter by constraints
        candidates = [v for v in versions if _satisfies(v, constraints)]
        if not candidates:
            raise ValueError(f"No available version for {name} matching {constraints}")
        # choose highest
        candidates.sort(key=lambda v: [int(x) for x in v.split(".")])
        version = candidates[-1]
        # already installed?
        if self.installed.get(name) == version:
            return
        # record reason
        if parent is None:
            self.reasons[name] = "user"
        else:
            self.reasons[name] = parent
        # install dependencies first
        deps = index[name][version].get("dependencies", [])
        for dep in deps:
            self.install(dep, offline=offline, parent=name)
        # now install
        self.installed[name] = version
        self.save()

    def freeze(self, lockfile_path):
        with open(lockfile_path, "w") as f:
            json.dump(self.installed, f, indent=2)

    def export_env(self, export_path):
        # identical to freeze
        self.freeze(export_path)

    def import_env(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        self.installed = data.copy()
        # reset reasons: all user-installed
        for pkg in self.installed:
            self.reasons[pkg] = "user"
        self.save()

    def list_updates(self):
        updates = {}
        for name, curver in self.installed.items():
            # if in remote
            if name in PACKAGE_INDEX:
                allv = list(PACKAGE_INDEX[name].keys())
                allv.sort(key=lambda v: [int(x) for x in v.split(".")])
                latest = allv[-1]
                if _compare_versions(latest, curver) == 1:
                    updates[name] = (curver, latest)
        return updates

    def check_vulnerabilities(self):
        vulns = {}
        for name, ver in self.installed.items():
            # check in remote first, then local
            if name in PACKAGE_INDEX and ver in PACKAGE_INDEX[name]:
                vs = PACKAGE_INDEX[name][ver].get("vulnerabilities", [])
            elif name in LOCAL_INDEX and ver in LOCAL_INDEX[name]:
                vs = LOCAL_INDEX[name][ver].get("vulnerabilities", [])
            else:
                vs = []
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
            if reason is None:
                break
            cur = reason
            if cur == "user":
                chain.append("user")
                break
        return chain
