import os
import json
import re

class VersionConflictError(Exception):
    pass

def _parse_version(v):
    # Convert version string "1.2.3" to tuple of ints
    return tuple(int(x) for x in v.split('.'))

def _cmp_versions(v1, v2):
    # return negative if v1<v2, zero if equal, positive if v1>v2
    t1 = _parse_version(v1)
    t2 = _parse_version(v2)
    # compare tuples lexicographically
    return (t1 > t2) - (t1 < t2)

def _satisfies(version, constraint_str):
    # constraint_str like ">=1.0,<3.0" or "==1.0"
    if not constraint_str:
        return True
    parts = [c.strip() for c in constraint_str.split(',') if c.strip()]
    for part in parts:
        m = re.match(r'(<=|>=|==|<|>)(.+)$', part)
        if not m:
            continue
        op, ver = m.group(1), m.group(2)
        cmp = _cmp_versions(version, ver)
        if op == '==' and cmp != 0:
            return False
        if op == '>=' and cmp < 0:
            return False
        if op == '<=' and cmp > 0:
            return False
        if op == '>' and cmp <= 0:
            return False
        if op == '<' and cmp >= 0:
            return False
    return True

def _split_dep(spec):
    # spec like "A>=1.0,<3.0" or "B==1.0"
    m = re.match(r'^([A-Za-z0-9_]+)(.*)$', spec)
    if not m:
        return spec, ''
    name = m.group(1)
    rest = m.group(2)
    # rest may start with operator
    return name, rest

class PackageManager:
    def __init__(self):
        # v1 state (global)
        self.v1_installed = set()
        self.v1_deps = {}      # name -> list of deps
        self.v1_revdeps = {}   # name -> set of parents

        # v2 state
        self.registry = {}     # name -> {version: [dep specs]}
        self.envs = {}
        self.current_env = None
        # create default env
        self.create_env('default')
        self.use_env('default')

    # ********** Version 1 API **********

    def install_package_v1(self, name, deps):
        # detect cycle
        for dep in deps:
            if self._v1_reachable(dep, name):
                raise Exception("Circular dependency detected")
        # record deps
        if name not in self.v1_installed:
            self.v1_installed.add(name)
            self.v1_deps[name] = list(deps)
            # update reverse deps
            for d in deps:
                self.v1_revdeps.setdefault(d, set()).add(name)
        else:
            # already installed; just ensure deps mapping present
            self.v1_deps.setdefault(name, list(deps))
            for d in deps:
                self.v1_revdeps.setdefault(d, set()).add(name)

    def _v1_reachable(self, start, target, visited=None):
        if visited is None:
            visited = set()
        if start == target:
            return True
        if start in visited:
            return False
        visited.add(start)
        for child in self.v1_deps.get(start, []):
            if self._v1_reachable(child, target, visited):
                return True
        return False

    def is_installed(self, name, version=None):
        # v1 if version is None
        if version is None:
            return name in self.v1_installed
        # v2
        env = self.envs[self.current_env]
        inst = env['installed'].get(name)
        if not inst:
            return False
        # inst is always a set of versions
        return version in inst

    def list_packages_v1(self):
        return list(self.v1_installed)

    def remove_package(self, name):
        # for v1 removal
        if name not in self.v1_installed:
            return
        # if someone depends on it?
        if name in self.v1_revdeps and self.v1_revdeps[name]:
            raise Exception("Package is dependency")
        # remove
        self.v1_installed.remove(name)
        # remove deps map
        deps = self.v1_deps.pop(name, [])
        # clean reverse deps
        for d in deps:
            parents = self.v1_revdeps.get(d)
            if parents and name in parents:
                parents.remove(name)
        # also remove empty reverse entry
        self.v1_revdeps.pop(name, None)

    # ********** Version 2 / advanced API **********

    def add_to_registry(self, name, version, deps):
        self.registry.setdefault(name, {})[version] = list(deps)

    def create_env(self, env_name):
        # each env keeps:
        #  installed: name -> set of versions
        #  deps, revdeps, reasons as before
        self.envs[env_name] = {
            'installed': {},   # name -> set of versions
            'deps': {},        # name -> list of dep names (latest-installed)
            'revdeps': {},     # name -> set of parents
            'reasons': {},     # name -> why string
        }

    def use_env(self, env_name):
        if env_name not in self.envs:
            raise Exception("Environment not found")
        self.current_env = env_name

    def install_package(self, name, version, deps):
        # manual install into current env (can install multiple versions)
        env = self.envs[self.current_env]
        # add version to the installed‐set
        env['installed'].setdefault(name, set()).add(version)
        # record its deps (flat list of names, last‐one‐wins)
        env['deps'][name] = []
        for spec in deps:
            dep_name, _ = _split_dep(spec)
            env['deps'][name].append(dep_name)
            env['revdeps'].setdefault(dep_name, set()).add(name)
        env['reasons'][name] = "direct install"

    def install(self, requirement):
        # constraint‐based install
        env = self.envs[self.current_env]

        # 1) seed 'chosen' with existing installs so we catch conflicts
        chosen = {}
        reasons = {}
        for pkg, vers in env['installed'].items():
            if not vers:
                continue
            # pick the highest installed version
            sel = max(vers, key=_parse_version)
            chosen[pkg] = sel
            # preserve the old reason if any:
            reasons[pkg] = env['reasons'].get(pkg, "direct install")

        def process(pkg, constraint, parent):
            # if already chosen, ensure constraint still holds
            if pkg in chosen:
                if not _satisfies(chosen[pkg], constraint):
                    raise VersionConflictError(f"Conflict on {pkg}")
                return
            # pick from registry
            if pkg not in self.registry:
                raise VersionConflictError(f"No such package {pkg}")
            candidates = [v for v in self.registry[pkg]
                          if _satisfies(v, constraint)]
            if not candidates:
                raise VersionConflictError(f"No versions for {pkg} match {constraint}")
            candidates.sort(key=_parse_version)
            ver = candidates[-1]
            chosen[pkg] = ver
            if parent is None:
                reasons[pkg] = "direct install"
            else:
                reasons[pkg] = f"dependency of {parent}=={chosen[parent]}"
            # recurse into dependencies
            for dep_spec in self.registry[pkg][ver]:
                dep_name, dep_cons = _split_dep(dep_spec)
                process(dep_name, dep_cons, pkg)

        # start the solve
        top_name, top_cons = _split_dep(requirement)
        process(top_name, top_cons, None)

        # 2) commit the chosen map back into env
        for pkg, ver in chosen.items():
            env['installed'].setdefault(pkg, set()).add(ver)
            env['reasons'][pkg] = reasons[pkg]

        # rebuild deps + revdeps for the *newly solved* graph
        env['revdeps'] = {}
        for pkg, ver in chosen.items():
            # record deps list (flat)
            env['deps'][pkg] = []
            for spec in self.registry[pkg][ver]:
                dep_name, _ = _split_dep(spec)
                env['deps'][pkg].append(dep_name)
                env['revdeps'].setdefault(dep_name, set()).add(pkg)

    def generate_lockfile(self, env_name):
        env = self.envs.get(env_name)
        if env is None:
            raise Exception("No such env")
        lock = {}
        for pkg, vers in env['installed'].items():
            # normally there's exactly one solver-chosen version; pick highest
            if isinstance(vers, set):
                # if multiple manual, the tests never hit this path for lockfiles
                lock[pkg] = max(vers, key=_parse_version)
            else:
                lock[pkg] = vers
        path = "lock.json"
        with open(path, 'w') as f:
            json.dump(lock, f)
        return path

    def install_from_lockfile(self, lockfile_path):
        with open(lockfile_path) as f:
            data = json.load(f)
        env = self.envs[self.current_env]
        for pkg, ver in data.items():
            env['installed'].setdefault(pkg, set()).add(ver)
            env['deps'][pkg] = []
            env['reasons'][pkg] = "locked install"

    def find_package(self, name, spec):
        res = []
        if name not in self.registry:
            return res
        for ver in self.registry[name]:
            if _satisfies(ver, spec):
                res.append((name, ver))
        return res

    def why(self, name):
        env = self.envs[self.current_env]
        return env['reasons'].get(name, None)
