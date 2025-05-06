import re
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, version_str):
        if not isinstance(version_str, str):
            raise ValueError("Version must be a string")
        parts = version_str.strip().split(".")
        if not all(part.isdigit() for part in parts):
            raise ValueError(f"Invalid version string: {version_str}")
        self.parts = tuple(int(p) for p in parts)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        for a, b in zip(self.parts, other.parts):
            if a != b:
                return a < b
        return len(self.parts) < len(other.parts)

    def __hash__(self):
        return hash(self.parts)

    def __str__(self):
        return ".".join(str(p) for p in self.parts)

    def __repr__(self):
        return f"Version('{self}')"

class Package:
    def __init__(self, name, version, dependencies=None):
        self.name = name
        self.version = Version(version)
        self.dependencies = dependencies or []

    def to_dict(self):
        return {
            "name": self.name,
            "version": str(self.version),
            "dependencies": [
                {"name": n, "version": v} for n, v in self.dependencies
            ],
        }

    def __repr__(self):
        deps = ", ".join(f"{n}@{v}" for n, v in self.dependencies)
        return f"Package({self.name}@{self.version}, deps=[{deps}])"

class Registry:
    def __init__(self):
        self._data = {}

    def add_package(self, name, version, dependencies=None):
        pkg = Package(name, version, dependencies)
        self._data.setdefault(name, {})
        if pkg.version in self._data[name]:
            raise ValueError(f"Package {name}@{version} already exists")
        self._data[name][pkg.version] = pkg

    def get_package(self, name, version):
        if name not in self._data:
            raise KeyError(f"Package {name} not found in registry")
        v = Version(version)
        if v not in self._data[name]:
            raise KeyError(f"Version {version} of package {name} not found")
        return self._data[name][v]

    def list_versions(self, name):
        if name not in self._data:
            return []
        return [str(v) for v in sorted(self._data[name].keys())]

    def search(self, name_substr=None, version_spec=None):
        result = []
        for pkg_name, versions in self._data.items():
            if name_substr and name_substr.lower() not in pkg_name.lower():
                continue
            for v, pkg in versions.items():
                if version_spec:
                    if version_spec.startswith(">="):
                        minv = Version(version_spec[2:])
                        if not (v >= minv):
                            continue
                    else:
                        if v != Version(version_spec):
                            continue
                result.append(pkg)
        return result
