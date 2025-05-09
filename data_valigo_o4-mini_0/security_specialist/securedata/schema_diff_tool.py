class SchemaDiffTool:
    @staticmethod
    def diff(old: dict, new: dict) -> dict:
        added = {k: new[k] for k in new if k not in old}
        removed = {k: old[k] for k in old if k not in new}
        changed = {
            k: {'old': old[k], 'new': new[k]}
            for k in old if k in new and old[k] != new[k]
        }
        return {'added': added, 'removed': removed, 'changed': changed}
