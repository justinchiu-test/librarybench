class Schema:
    def __init__(self, fields: dict, parent: 'Schema' = None):
        self.parent = parent
        if parent:
            merged = dict(parent.fields)
            merged.update(fields)
            self.fields = merged
        else:
            self.fields = dict(fields)

    def validate(self, data: dict) -> bool:
        # simple type check
        for k, t in self.fields.items():
            if k not in data:
                raise ValueError(f"Missing field {k}")
            if not isinstance(data[k], t):
                raise TypeError(f"Field {k} expected {t}, got {type(data[k])}")
        return True

class VersionedSchema(Schema):
    def __init__(self, fields: dict, version: int, parent: 'VersionedSchema' = None):
        super().__init__(fields, parent)
        self.version = version
        self._migrations = {}  # mapping from version to fn

    def add_migration(self, from_version: int, fn):
        self._migrations[from_version] = fn

    def migrate(self, data: dict, target_version: int) -> dict:
        cur = self.version
        # Disallow backward migrations unless explicitly defined (not supported here)
        if target_version < cur:
            raise ValueError(f"No migration from {cur} to {target_version}")
        # Apply forward migrations step by step
        result = dict(data)
        for v in range(cur, target_version):
            fn = self._migrations.get(v)
            if not fn:
                raise ValueError(f"No migration from {v}")
            result = fn(result)
        return result
