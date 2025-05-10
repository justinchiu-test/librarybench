class SchemaDiffTool:
    @staticmethod
    def diff(old_schema: dict, new_schema: dict) -> dict:
        old_fields = set(old_schema.keys())
        new_fields = set(new_schema.keys())
        added = new_fields - old_fields
        removed = old_fields - new_fields
        changed = {
            field for field in old_fields & new_fields
            if old_schema[field] != new_schema[field]
        }
        return {
            'added': sorted(list(added)),
            'removed': sorted(list(removed)),
            'changed': sorted(list(changed)),
        }
