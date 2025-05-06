"""
registry.py

Implements an in-memory package registry with search and metadata APIs.
"""
from typing import List, Optional, Dict
from .models import Package, Metadata
from utils import compare_versions, parse_constraints, satisfies_constraints, parse_version

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
        return sorted(self._data[name].keys(), key=parse_version)

    def get_metadata(self, name: str, version: str) -> Optional[Metadata]:
        return self._data.get(name, {}).get(version)

    def search(self, name_pattern: str = "", version_spec: Optional[str] = None) -> List[Package]:
        """
        Search packages by name substring and optional version specification.
        """
        results: List[Package] = []
        # parse constraints if any
        cons = [] if version_spec is None else parse_constraints(version_spec)[1]
        for name, versions in self._data.items():
            if name_pattern.lower() not in name.lower():
                continue
            matched = [v for v in versions if
                       (version_spec is None) or satisfies_constraints(v, cons)]
            if not matched:
                continue
            if version_spec is None:
                latest = max(matched, key=parse_version)
                results.append(Package(name, self._data[name][latest]))
            else:
                for v in matched:
                    results.append(Package(name, self._data[name][v]))
        return results
