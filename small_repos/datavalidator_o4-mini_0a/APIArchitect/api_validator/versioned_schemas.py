class VersionedSchemas:
    def __init__(self):
        self.schemas = {}

    def register(self, version, schema):
        self.schemas[version] = schema

    def get(self, version):
        return self.schemas.get(version)

    def migrate(self, data, from_version, to_version):
        if from_version == to_version:
            return data
        raise NotImplementedError("Migration path not implemented")
