from registry import Registry, Version

class PackageManager:
    def __init__(self, registry=None):
        self.registry = registry or Registry()
        self.installed = {}

    def install(self, name, version):
        pkg = self.registry.get_package(name, version)
        for dep_name, dep_version in pkg.dependencies:
            if not (dep_name in self.installed and self.installed[dep_name] == Version(dep_version)):
                self.install(dep_name, dep_version)
        self.installed[name] = Version(str(pkg.version))

    def list_installed(self):
        return {n: str(v) for n, v in self.installed.items()}

    def show_metadata(self, name, version):
        root = self.registry.get_package(name, version)
        deps = [{"name": n, "version": v} for n, v in root.dependencies]
        version_strings = set(self.registry.list_versions(name)) | {version}
        pending = [(name, version)]
        visited = set()
        while pending:
            pkg_name, pkg_version = pending.pop(0)
            if (pkg_name, pkg_version) in visited:
                continue
            visited.add((pkg_name, pkg_version))
            try:
                obj = self.registry.get_package(pkg_name, pkg_version)
            except KeyError:
                continue
            for dn, dv in obj.dependencies:
                pending.append((dn, dv))
                if dn == name:
                    version_strings.add(dv)
        history = [str(v) for v in sorted(Version(vs) for vs in version_strings)]
        return {"name": name, "version": version,
                "dependencies": deps, "version_history": history}

    def check_updates(self):
        result = {}
        for name, curr_v in self.installed.items():
            versions = self.registry.list_versions(name)
            if not versions:
                continue
            latest = Version(versions[-1])
            if latest > curr_v:
                result[name] = (str(curr_v), str(latest))
        return result
