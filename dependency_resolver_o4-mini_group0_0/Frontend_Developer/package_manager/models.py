"""
models.py

Defines the Package and Metadata data structures.
"""

from typing import Dict, List

class Metadata:
    def __init__(self, version: str, dependencies: List[str]):
        self.version = version
        self.dependencies = dependencies

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "dependencies": list(self.dependencies),
        }

    def __eq__(self, other):
        if not isinstance(other, Metadata):
            return False
        return (self.version == other.version and
                self.dependencies == other.dependencies)

    def __repr__(self):
        return f"Metadata(version={self.version!r}, dependencies={self.dependencies!r})"

class Package:
    def __init__(self, name: str, metadata: Metadata):
        self.name = name
        self.metadata = metadata

    def __repr__(self):
        return f"Package(name={self.name!r}, metadata={self.metadata!r})"

    def to_dict(self):
        return {"name": self.name, **self.metadata.to_dict()}
