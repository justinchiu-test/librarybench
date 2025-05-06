import datetime


class VersionedEntity:
    """
    Mixin to add version tracking to workflows or other entities.
    """
    def __init__(self):
        self._versions = []  # list of (timestamp, snapshot)
        self._current = None

    def save_version(self, snapshot):
        ts = datetime.datetime.utcnow()
        self._versions.append((ts, snapshot))
        self._current = snapshot

    @property
    def versions(self):
        return list(self._versions)

    @property
    def current(self):
        return self._current

    def rollback(self, index: int):
        if index < 0 or index >= len(self._versions):
            raise IndexError("Invalid version index")
        ts, snapshot = self._versions[index]
        self._current = snapshot
        self._versions = self._versions[: index + 1]
        return snapshot
