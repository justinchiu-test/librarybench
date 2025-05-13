import copy

class Versioning:
    def __init__(self):
        self.versions = {}

    def record_version(self, stage_name, version_name, data):
        self.versions.setdefault(stage_name, []).append((version_name, copy.deepcopy(data)))

    def get_versions(self, stage_name):
        return [v for v, _ in self.versions.get(stage_name, [])]

    def get_data(self, stage_name, version_name):
        for v, d in self.versions.get(stage_name, []):
            if v == version_name:
                return copy.deepcopy(d)
        raise KeyError(f"Version {version_name} not found for stage {stage_name}")
