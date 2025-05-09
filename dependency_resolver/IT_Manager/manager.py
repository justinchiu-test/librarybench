from registry import Registry, Version

class PackageManager:
    def __init__(self, registry=None):
        self.registry = registry or Registry()
        # installed: name -> Version
        self.installed = {}

    def install(self, name, version):
        """
        Recursively installs a package and its dependencies.
        """
        pkg = self.registry.get_package(name, version)
        # install dependencies first
        for dep_name, dep_version in pkg.dependencies:
            if dep_name in self.installed and self.installed[dep_name] == Version(dep_version):
                continue
            self.install(dep_name, dep_version)
        # install this package
        self.installed[name] = Version(str(pkg.version))

    def list_installed(self):
        """
        Returns dict of name->version_str
        """
        return {n: str(v) for n, v in self.installed.items()}

    def show_metadata(self, name, version):
        """
        Returns dict: name, version, dependencies, version_history

        version_history is the full list of past versions of `name`,
        drawing from both the registry’s own versions and any self‐references
        in the dependency chain of the requested version.
        """
        # get the Package object (or KeyError if missing)
        root_pkg = self.registry.get_package(name, version)
        # dump its immediate dependencies
        deps = [{"name": n, "version": v} for (n, v) in root_pkg.dependencies]

        # start with all registry versions of `name` plus the requested version
        version_strings = set(self.registry.list_versions(name))
        version_strings.add(version)

        # walk the dependency graph to catch any "hidden" self‐references
        # pending: list of (pkg_name, pkg_version) to explore
        pending = [(name, version)]
        visited = set()

        while pending:
            pkg_name, pkg_version = pending.pop(0)
            if (pkg_name, pkg_version) in visited:
                continue
            visited.add((pkg_name, pkg_version))
            try:
                pkg_obj = self.registry.get_package(pkg_name, pkg_version)
            except KeyError:
                # if it's not in the registry, we still record it when self‐referenced
                continue
            for dep_name, dep_version in pkg_obj.dependencies:
                # always explore deeper so we can find nested self‐refs
                pending.append((dep_name, dep_version))
                # if we see the same package name, record that version
                if dep_name == name:
                    version_strings.add(dep_version)

        # sort them by Version and stringify
        history = [str(v) for v in sorted(Version(vs) for vs in version_strings)]

        return {
            "name": name,
            "version": version,
            "dependencies": deps,
            "version_history": history,
        }

    def check_updates(self):
        """
        Returns dict name->(current_version_str, latest_version_str)
        for those with updates.
        """
        result = {}
        for name, curr_v in self.installed.items():
            versions = self.registry.list_versions(name)
            if not versions:
                continue
            latest = Version(versions[-1])
            if latest > curr_v:
                result[name] = (str(curr_v), str(latest))
        return result
