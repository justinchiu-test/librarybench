# coding: utf-8
"""
Simple TOML dump wrapper for tests
"""
try:
    import toml as _toml_lib
    dumps = _toml_lib.dumps
    # toml_lib may support loads
    loads = getattr(_toml_lib, 'loads', None)
except ImportError:
    def dumps(data):
        # Simple implementation: flat keys and single-level tables
        lines = []
        # top-level scalars
        for k, v in list(data.items()):
            if not isinstance(v, dict):
                val = f"'{v}'" if isinstance(v, str) else v
                lines.append(f"{k} = {val}")
        # tables
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"[{k}]")
                for ik, iv in v.items():
                    val = f"'{iv}'" if isinstance(iv, str) else iv
                    lines.append(f"{ik} = {val}")
        return '\n'.join(lines)
    loads = None