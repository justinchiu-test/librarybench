import os
import json
import configparser
try:
    import yaml
except ImportError:
    yaml = None
try:
    import toml
except ImportError:
    toml = None

def env_override(config):
    prefix = "OSS_"
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        key = k[len(prefix):].lower()
        config[key] = v
    return config

def load_config(paths):
    config = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        ext = os.path.splitext(p)[1].lower()
        if ext == ".ini":
            parser = configparser.ConfigParser()
            parser.read(p)
            for section in parser.sections():
                config.setdefault(section, {})
                for k, v in parser.items(section):
                    config[section][k] = v
        elif ext == ".json":
            with open(p) as f:
                data = json.load(f)
            if isinstance(data, dict):
                config.update(data)
        elif ext in (".yaml", ".yml") and yaml:
            with open(p) as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                config.update(data)
        elif ext == ".toml" and toml:
            with open(p) as f:
                data = toml.load(f)
            if isinstance(data, dict):
                config.update(data)
    return env_override(config)
