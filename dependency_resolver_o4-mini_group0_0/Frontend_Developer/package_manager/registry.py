"""
registry.py

Implements an in-memory package registry with search and metadata APIs.
"""

from typing import List, Optional, Dict, Tuple
from .models import Package, Metadata
from utils import compare_versions

class Registry:
    """
    A simple in-memory registry of packages.
    """
    def __init__(self):
        # sample data
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
        return sorted(self._data[name].keys(),
                      key=lambda v: [int(x) for x in v.split(".")])

    def get_metadata(self, name: str, version: str) -> Optional[Metadata]:
        return self._data.get(name, {}).get(version)

    def search(self, name_pattern: str = "", version_spec: Optional[str] = None) -> List[Package]:
        results: List[Package] = []
        for name, versions in self._data.items():
            if name_pattern.lower() not in name.lower():
                continue
            matched = []
            if version_spec is None:
                matched = list(versions.keys())
            else:
                op, ver = self._parse_spec(version_spec)
                for v in versions:
                    cmp = compare_versions(v, ver)
                    if ((op == "==" and cmp == 0) or
                        (op == ">=" and cmp >= 0) or
                        (op == "<=" and cmp <= 0) or
                        (op == ">" and cmp > 0) or
                        (op == "<" and cmp < 0)):
                        matched.append(v)
            if not matched:
                continue
            if version_spec is None:
                latest = sorted(matched, key=lambda x: [int(y) for y in x.split(".")])[-1]
                results.append(Package(name, versions[latest]))
            else:
                for v in matched:
                    results.append(Package(name, versions[v]))
        return results

    def _parse_spec(self, spec: str) -> Tuple[str, str]:
        for op in ["==", ">=", "<=", ">", "<"]:
            if spec.startswith(op):
                return op, spec[len(op):]
        return "==", spec
