class Schema:
    def __init__(self, fields: dict, parent: 'Schema' = None):
        self.parent = parent
        self.fields = fields or {}

    def resolved_fields(self) -> dict:
        if self.parent:
            resolved = self.parent.resolved_fields().copy()
            resolved.update(self.fields)
            return resolved
        return self.fields.copy()
