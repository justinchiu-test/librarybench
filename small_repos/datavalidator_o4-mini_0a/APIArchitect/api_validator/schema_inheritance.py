class SchemaInheritance:
    @staticmethod
    def extend_schema(base_schema, overrides):
        schema = base_schema.copy()
        schema.update(overrides)
        return schema
