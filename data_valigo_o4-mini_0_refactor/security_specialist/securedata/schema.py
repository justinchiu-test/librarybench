class Schema:
    def __init__(self, name, fields, version=1, parent=None):
        self.name = name
        self.fields = dict(fields)
        self.version = version
        self.parent = parent
        if parent:
            merged = dict(parent.fields)
            merged.update(self.fields)
            self.fields = merged

    def migrate(self, new_fields, new_version):
        return Schema(self.name, new_fields, new_version, parent=self)

class SchemaRegistry:
    def __init__(self):
        self.schemas = {}

    def register(self, schema: Schema):
        self.schemas.setdefault(schema.name, {})[schema.version] = schema

    def get(self, name, version):
        return self.schemas.get(name, {}).get(version)
