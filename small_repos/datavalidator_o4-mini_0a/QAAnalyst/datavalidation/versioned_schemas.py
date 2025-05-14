class VersionedSchemas:
    def __init__(self):
        # Example schemas with required and optional fields
        self.schemas = {
            1: {'required': ['id', 'name'], 'optional': []},
            2: {'required': ['id', 'name', 'email'], 'optional': ['age']},
        }

    def get_schema(self, version):
        return self.schemas.get(version)
