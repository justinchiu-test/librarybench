"""
manager.py

Handles pinning/unpinning packages, and saving/loading pins to a file.
"""

from typing import Dict, Optional
from .registry import Registry


class PackageManager:
    def __init__(self, registry: Registry):
        self.registry = registry
        # name -> version
        self._pins: Dict[str, str] = {}

    def pin(self, name: str, version: str) -> None:
        """
        Pin a package to a specific version.
        """
        metadata = self.registry.get_metadata(name, version)
        if metadata is None:
            raise ValueError(f"Package {name} version {version} not found in registry.")
        self._pins[name] = version

    def unpin(self, name: str) -> None:
        """
        Unpin a package.
        """
        if name in self._pins:
            del self._pins[name]

    def list_pins(self) -> Dict[str, str]:
        """
        Return a dict of pinned packages.
        """
        return dict(self._pins)

    def update(self, name: str, new_version: str) -> None:
        """
        Update an existing pin to a different version.
        """
        if name not in self._pins:
            raise KeyError(f"Package {name} is not pinned.")
        self.pin(name, new_version)

    def save_pins(self, file_path: str) -> None:
        """
        Save pinned packages to a requirements-style file.
        """
        lines = [f"{name}=={ver}" for name, ver in sorted(self._pins.items())]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load_pins(self, file_path: str) -> None:
        """
        Load pinned packages from a requirements-style file.
        Existing pins are cleared.
        """
        self._pins.clear()
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "==" not in line:
                    continue
                name, ver = line.split("==", 1)
                # validate
                if self.registry.get_metadata(name, ver) is None:
                    raise ValueError(f"Package {name}=={ver} not found in registry.")
                self._pins[name] = ver
