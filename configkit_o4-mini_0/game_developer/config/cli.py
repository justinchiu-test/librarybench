def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

class CLIConfigGenerator:
    @staticmethod
    def generate(config):
        flat = flatten_dict(config)
        cmds = []
        for key, val in flat.items():
            cmds.append(f"gamectl set {key} {val}")
        return cmds
