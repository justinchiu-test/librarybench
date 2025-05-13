import os
import importlib.util

def load_plugins(path):
    results = {}
    for root, dirs, files in os.walk(path):
        for fname in files:
            if not fname.endswith('.py') or fname.startswith('_'):
                continue
            full = os.path.join(root, fname)
            name = os.path.splitext(os.path.relpath(full, path))[0].replace(os.sep, '.')
            spec = importlib.util.spec_from_file_location(name, full)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'load'):
                results[name] = mod.load()
    return results
