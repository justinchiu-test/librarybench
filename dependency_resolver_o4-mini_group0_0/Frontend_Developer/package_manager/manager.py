"""
manager.py

Handles pinning/unpinning packages, and saving/loading pins to a file.
"""

from typing import Dict, Optional
from .registry import Registry
from utils import read_lines, write_lines, parse_pin_line

class PackageManager:
    def __init__(self, registry: Registry):
        self.registry = registry
        self._pins: Dict[str, str] = {}

    def pin(self, name: str, version: str) -> None:
        metadata = self.registry.get_metadata(name, version)
        if metadata is None:
            raise ValueError(f"Package {name} version {version} not found in registry.")
        self._pins[name] = version

    def unpin(self, name: str) -> None:
        self._pins.pop(name, None)

    def list_pins(self) -> Dict[str, str]:
        return dict(self._pins)

    def update(self, name: str, new_version: str) -> None:
        if name not in self._pins:
            raise KeyError(f"Package {name} is not pinned.")
        self.pin(name, new_version)

    def save_pins(self, file_path: str) -> None:
        lines = [f"{name}=={ver}" for name, ver in sorted(self._pins.items())]
        write_lines(file_path, lines)

    def load_pins(self, file_path: str) -> None:
        self._pins.clear()
        for line in read_lines(file_path):
            if not line or line.startswith("#"):
                continue
            if "==" not in line:
                continue
            name, ver = parse_pin_line(line)
            if self.registry.get_metadata(name, ver) is None:
                raise ValueError(f"Package {name}=={ver} not found in registry.")
            self._pins[name] = ver
