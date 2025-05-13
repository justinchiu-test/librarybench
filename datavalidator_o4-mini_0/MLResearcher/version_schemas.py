class VersionedSchemas:
    def __init__(self):
        self.schemas = {}
        self.migrations = {}

    def add_schema(self, version, schema):
        self.schemas[version] = schema

    def get_schema(self, version):
        return self.schemas.get(version)

    def add_migration(self, from_version, to_version, func):
        self.migrations[(from_version, to_version)] = func

    def migrate(self, data, from_version, to_version):
        if from_version == to_version:
            return data
        key = (from_version, to_version)
        if key not in self.migrations:
            raise ValueError(f"No migration from {from_version} to {to_version}")
        return self.migrations[key](data)
