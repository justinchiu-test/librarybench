import os
import json
import configparser

class ConfigManager:
    def __init__(self):
        self.global_schema = {'required': [], 'defaults': {}}
        self.project_schema = {'required': [], 'defaults': {}}
        self.user_schema = {'required': [], 'defaults': {}}
        self.plugin_schemas = {}
        self.plugins = {}
        self.validation_mode = 'interactive'

    def inherit_schema(self, base, override):
        result = base.copy()
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self.inherit_schema(result[k], v)
            else:
                result[k] = v
        return result

    def lazy_load_section(self, config, section):
        if section not in config or section not in self.plugins:
            return
        plugin = self.plugins[section]
        if plugin.get('_loaded'):
            return
        raw = config.get(section, {})
        loader = plugin.get('loader')
        if loader:
            processed = loader(raw)
            config[section] = processed
        plugin['_loaded'] = True

    def set_validation_context(self, mode):
        if mode not in ('interactive', 'ci'):
            raise ValueError("Invalid validation mode")
        self.validation_mode = mode

    def load_config(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.json':
            with open(file_path, 'r') as f:
                return json.load(f)
        elif ext in ('.ini', '.cfg'):
            parser = configparser.ConfigParser()
            parser.read(file_path)
            result = {}
            for sec in parser.sections():
                result[sec] = dict(parser.items(sec))
            return result
        else:
            raise ValueError("Unsupported config format")

    def load_env_file(self):
        path = os.path.join(os.getcwd(), '.env')
        env = {}
        if not os.path.isfile(path):
            return env
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                env[k] = v
        return env

    def register_plugin(self, name, schema=None, loader=None, validator=None, post_process=None):
        self.plugins[name] = {
            'schema': schema or {'required': [], 'defaults': {}},
            'loader': loader,
            'validator': validator,
            'post_process': post_process
        }
        self.plugin_schemas[name] = self.plugins[name]['schema']

    def apply_defaults(self, config):
        for schema in [self.global_schema, self.project_schema, self.user_schema] + list(self.plugin_schemas.values()):
            for k, v in schema.get('defaults', {}).items():
                if k not in config:
                    config[k] = v

    def compose_schemas(self):
        combined = {'required': [], 'defaults': {}}
        for schema in [self.global_schema, self.project_schema, self.user_schema] + list(self.plugin_schemas.values()):
            for r in schema.get('required', []):
                if r not in combined['required']:
                    combined['required'].append(r)
            for k, v in schema.get('defaults', {}).items():
                combined['defaults'][k] = v
        return combined

    def expand_env_vars(self, config):
        def _expand(val):
            if isinstance(val, str):
                return os.path.expandvars(val)
            if isinstance(val, dict):
                return {k: _expand(v) for k, v in val.items()}
            if isinstance(val, list):
                return [_expand(v) for v in val]
            return val
        return _expand(config)

    def prompt_for_missing(self, config):
        schema = self.compose_schemas()
        for k in schema['required']:
            if k not in config or config[k] is None:
                val = input(f"Enter value for {k}: ")
                config[k] = val

    def validate(self, config):
        schema = self.compose_schemas()
        missing = [k for k in schema['required'] if k not in config or config[k] is None]
        if missing and self.validation_mode == 'ci':
            raise ValueError(f"Missing required config fields: {missing}")
        for name, plugin in self.plugins.items():
            validator = plugin.get('validator')
            if validator and name in config:
                validator(config[name])
