class SchemaDiffTool:
    @staticmethod
    def compute_diff(schema1: dict, schema2: dict) -> dict:
        added = {k: schema2[k] for k in schema2 if k not in schema1}
        removed = {k: schema1[k] for k in schema1 if k not in schema2}
        changed = {k: (schema1[k], schema2[k]) for k in schema1 if k in schema2 and schema1[k] != schema2[k]}
        return {"added": added, "removed": removed, "changed": changed}
