class TestDataGenerator:
    def __init__(self, schema, aliases=None):
        self.schema = schema
        self.aliases = aliases or {}

    def generate_valid(self):
        return self._build(self.schema, valid=True)

    def generate_invalid(self):
        return self._build(self.schema, valid=False)

    def generate_minimal(self):
        return self._build_min_max(self.schema, minimal=True)

    def generate_maximal(self):
        return self._build_min_max(self.schema, minimal=False)

    def _build(self, schema, valid):
        typ = schema.get('type')
        if typ == 'object':
            obj = {}
            props = schema.get('properties', {})
            required = schema.get('required', [])
            for prop, subschema in props.items():
                if valid or prop in required:
                    obj[prop] = self._build(subschema, valid)
            return obj
        elif typ == 'integer':
            return 1 if valid else 'invalid'
        elif typ == 'string':
            return 'a' if valid else 123
        elif typ == 'boolean':
            return True if valid else 'notbool'
        return None

    def _build_min_max(self, schema, minimal):
        typ = schema.get('type')
        if typ == 'object':
            obj = {}
            props = schema.get('properties', {})
            required = schema.get('required', [])
            for prop, subschema in props.items():
                if prop in required or not minimal:
                    obj[prop] = self._build_min_max(subschema, minimal)
            return obj
        elif typ == 'integer':
            if minimal:
                return schema.get('minimum', 0)
            return schema.get('maximum', 100)
        elif typ == 'string':
            if minimal:
                minl = schema.get('minLength', 1)
                return 'a' * minl
            maxl = schema.get('maxLength', 10)
            return 'a' * maxl
        elif typ == 'boolean':
            return False if minimal else True
        return None
