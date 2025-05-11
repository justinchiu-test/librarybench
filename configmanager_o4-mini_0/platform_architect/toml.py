"""
Minimal TOML dumping implementation to support tests that do:
    import toml as _toml
    _toml.dumps(data_dict)
"""
def dumps(data):
    lines = []
    def recurse(d, prefix=None):
        # if nested dict, write table header
        for k, v in d.items():
            if isinstance(v, dict):
                newprefix = k if prefix is None else f"{prefix}.{k}"
                lines.append(f"[{newprefix}]")
                recurse(v, newprefix)
            else:
                if isinstance(v, str):
                    val = f'"{v}"'
                elif isinstance(v, bool):
                    val = "true" if v else "false"
                else:
                    val = str(v)
                lines.append(f"{k} = {val}")
    recurse(data)
    return "\n".join(lines) + "\n"
