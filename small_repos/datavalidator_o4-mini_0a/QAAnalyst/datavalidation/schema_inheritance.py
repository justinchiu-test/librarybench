from .versioned_schemas import VersionedSchemas

class SchemaInheritance(VersionedSchemas):
    def extend_schema(self, version, overrides):
        base = self.get_schema(version)
        if base is None:
            return overrides
        schema = {**base}
        # Merge required and optional lists if provided in overrides
        for key in ['required', 'optional']:
            if key in overrides:
                schema[key] = base.get(key, []) + overrides[key]
        return schema
