class DefaultValues:
    def apply_defaults(self, data, schema):
        for field, props in schema.items():
            if field not in data and 'default' in props:
                data[field] = props['default']
        return data
