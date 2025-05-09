class SchemaRegistry:
    def __init__(self):
        self._schemas = {}

    def register(self, schema: dict, version: str):
        if version in self._schemas:
            raise ValueError(f"Schema version '{version}' already registered.")
        if not isinstance(schema, dict):
            raise TypeError("Schema must be a dict.")
        # Store a copy to avoid external mutation
        self._schemas[version] = schema.copy()

    def get_schema(self, version: str) -> dict:
        if version not in self._schemas:
            raise KeyError(f"Schema version '{version}' not found.")
        return self._schemas[version].copy()

    def migrate(self, data: dict, from_version: str, to_version: str) -> dict:
        if from_version not in self._schemas:
            raise KeyError(f"Schema version '{from_version}' not found.")
        if to_version not in self._schemas:
            raise KeyError(f"Schema version '{to_version}' not found.")
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict.")
        old_schema = self._schemas[from_version]
        new_schema = self._schemas[to_version]
        migrated = {}
        # Include only fields in new schema; fill defaults
        for key, default in new_schema.items():
            migrated[key] = data.get(key, default)
        return migrated

# Global registry instance
registry = SchemaRegistry()

def schema_versioning(schema: dict, version: str):
    """
    Register a new schema version.
    """
    registry.register(schema, version)

def migrate(data: dict, from_version: str, to_version: str) -> dict:
    """
    Migrate data from one version to another.
    """
    return registry.migrate(data, from_version, to_version)
