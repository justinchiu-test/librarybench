"""
registry.py

Implements an in-memory package registry with search and metadata APIs.
"""

from typing import List, Optional, Dict, Tuple
from .models import Package, Metadata


def compare_versions(v1: str, v2: str) -> int:
    """
    Compares two semantic version strings.
    Returns -1 if v1<v2, 0 if equal, +1 if v1>v2.
    """
    parts1 = [int(p) for p in v1.split(".")]
    parts2 = [int(p) for p in v2.split(".")]
    # Normalize lengths
    length = max(len(parts1), len(parts2))
    parts1 += [0] * (length - len(parts1))
    parts2 += [0] * (length - len(parts2))
    for a, b in zip(parts1, parts2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


class Registry:
    """
    A simple in-memory registry of packages.
    """

    def __init__(self):
        # sample data
        # name -> version -> metadata dict
        self._data: Dict[str, Dict[str, Metadata]] = {
            "packageA": {
                "1.0.0": Metadata("1.0.0", []),
                "1.1.0": Metadata("1.1.0", ["packageB>=2.0.0"]),
                "2.0.0": Metadata("2.0.0", ["packageC>=1.0.0", "packageA>=1.0.0"]),
            },
            "packageB": {
                "1.0.0": Metadata("1.0.0", []),
                "2.0.0": Metadata("2.0.0", []),
            },
            "packageC": {
                "1.0.0": Metadata("1.0.0", []),
            },
        }

    def list_packages(self) -> List[str]:
        return sorted(self._data.keys())

    def list_versions(self, name: str) -> List[str]:
        if name not in self._data:
            return []
        return sorted(self._data[name].keys(), key=lambda v: [int(x) for x in v.split(".")])

    def get_metadata(self, name: str, version: str) -> Optional[Metadata]:
        return self._data.get(name, {}).get(version)

    def search(self, name_pattern: str = "", version_spec: Optional[str] = None) -> List[Package]:
        """
        Search packages by name substring and optional version specification.
        version_spec forms supported: ==1.0.0, >=1.0.0, <=2.0.0, >1.0.0, <2.0.0
        If version_spec is None, returns the latest version for each matching package.
        """
        results: List[Package] = []
        for name, versions in self._data.items():
            if name_pattern.lower() not in name.lower():
                continue
            matched_versions = []
            for v in versions:
                if version_spec is None:
                    matched_versions.append(v)
                else:
                    op, ver = self._parse_spec(version_spec)
                    cmp = compare_versions(v, ver)
                    if op == "==":
                        if cmp == 0:
                            matched_versions.append(v)
                    elif op == ">=":
                        if cmp >= 0:
                            matched_versions.append(v)
                    elif op == "<=":
                        if cmp <= 0:
                            matched_versions.append(v)
                    elif op == ">":
                        if cmp > 0:
                            matched_versions.append(v)
                    elif op == "<":
                        if cmp < 0:
                            matched_versions.append(v)
            if not matched_versions:
                continue
            # if no spec, pick latest
            if version_spec is None:
                latest = sorted(matched_versions, key=lambda x: [int(y) for y in x.split(".")])[-1]
                results.append(Package(name, self._data[name][latest]))
            else:
                for mv in matched_versions:
                    results.append(Package(name, self._data[name][mv]))
        return results

    def _parse_spec(self, spec: str) -> Tuple[str, str]:
        for op in ["==", ">=", "<=", ">", "<"]:
            if spec.startswith(op):
                return op, spec[len(op) :]
        # default to equality
        return "==", spec
