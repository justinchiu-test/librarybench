import os
import json
import configparser

# YAML support, with a minimal fallback parser if PyYAML is not installed
try:
    import yaml as _yaml_module
except ImportError:
    class _DummyYAML:
        @staticmethod
        def safe_load(f):
            text = f.read()
            result = {}
            current_section = None
            for line in text.splitlines():
                if not line.strip():
                    continue
                indent = len(line) - len(line.lstrip(' '))
                # Top‐level mapping
                if indent == 0 and line.rstrip().endswith(':'):
                    key = line.rstrip()[:-1].strip()
                    result[key] = {}
                    current_section = result[key]
                # One level nested mapping
                elif indent > 0 and current_section is not None:
                    stripped = line.strip()
                    if ':' in stripped:
                        k, v = stripped.split(':', 1)
                        current_section[k.strip()] = v.strip()
            return result
    yaml = _DummyYAML()
else:
    yaml = _yaml_module

# TOML support, with a minimal fallback parser if 'toml' is not installed
try:
    import toml as _toml_module
except ImportError:
    class _DummyToml:
        @staticmethod
        def load(f):
            text = f.read()
            result = {}
            current_section = result
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Section headers like [section]
                if line.startswith('[') and line.endswith(']'):
                    sec = line[1:-1].strip()
                    result[sec] = {}
                    current_section = result[sec]
                # Key = value lines
                elif '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v_str = v.strip()
                    # String literal
                    if (v_str.startswith('"') and v_str.endswith('"')) or \
                       (v_str.startswith("'") and v_str.endswith("'")):
                        v_val = v_str[1:-1]
                    else:
                        # Try integer
                        try:
                            v_val = int(v_str)
                        except ValueError:
                            # Try float
                            try:
                                v_val = float(v_str)
                            except ValueError:
                                v_val = v_str
                    current_section[k] = v_val
            return result
    toml = _DummyToml()
else:
    toml = _toml_module


def load_config(path):
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext == '.json':
        with open(path) as f:
            return json.load(f)
    elif ext in ('.yml', '.yaml'):
        # Use yaml.safe_load (PyYAML) or our fallback
        with open(path) as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        # Use toml.load or our fallback
        with open(path) as f:
            return toml.load(f)
    elif ext in ('.ini',):
        config = configparser.ConfigParser()
        config.read(path)
        return {section: dict(config[section]) for section in config.sections()}
    else:
        raise ValueError(f"Unsupported config format: {ext}")
