class SchemaEnforcement:
    def __init__(self, initial_schema=None, allow_new_fields=False):
        self.schema = dict(initial_schema or {})
        self.allow_new_fields = allow_new_fields

    def enforce(self, record):
        # check required fields and types
        for field, typ in self.schema.items():
            if field not in record or not isinstance(record[field], typ):
                raise ValueError(f"Field {field} missing or wrong type")
        # check for unexpected fields
        if not self.allow_new_fields:
            for field in record:
                if field not in self.schema:
                    raise ValueError(f"Unexpected field {field}")
        return record

    def update_schema(self, new_schema):
        # no breaking changes: type of existing fields must not change
        for field, typ in new_schema.items():
            if field in self.schema and self.schema[field] is not typ:
                raise ValueError(f"Breaking change for field {field}")
        self.schema.update(new_schema)
        return self.schema
