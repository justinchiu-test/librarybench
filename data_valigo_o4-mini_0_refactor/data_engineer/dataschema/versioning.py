class SchemaVersioning:
    def __init__(self):
        # {version: schema_fields}
        self._schemas = {}
        # migrations: {(from_v, to_v): func}
        self._migrations = {}

    def register(self, version: str, schema_fields: dict):
        self._schemas[version] = schema_fields

    def add_migration(self, from_v: str, to_v: str, func):
        self._migrations[(from_v, to_v)] = func

    def validate(self, version: str, data: dict) -> bool:
        schema = self._schemas.get(version)
        if schema is None:
            raise ValueError("Unknown version")
        # simple key presence check
        for key in schema:
            if key not in data:
                return False
        return True

    def migrate(self, data: dict, from_v: str, to_v: str) -> dict:
        if from_v == to_v:
            return data.copy()
        func = self._migrations.get((from_v, to_v))
        if not func:
            raise ValueError("Migration path not found")
        return func(data.copy())
