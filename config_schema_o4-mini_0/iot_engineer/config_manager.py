import os
import json
import configparser

class ConfigManager:
    def __init__(self):
        self.config = {}
        self._loaders = {}
        self.plugins = []
        self.env_vars = {}
        self.validation_context = None

    def inherit_schema(self, base, override):
        """
        Deep-merge two dicts: keys in override replace or merge into base.
        """
        merged = {}
        # First, take keys from base
        for key, base_val in base.items():
            if key in override:
                over_val = override[key]
                if isinstance(base_val, dict) and isinstance(over_val, dict):
                    merged[key] = self.inherit_schema(base_val, over_val)
                else:
                    merged[key] = over_val
            else:
                merged[key] = base_val
        # Then any keys only in override
        for key, over_val in override.items():
            if key not in base:
                merged[key] = over_val
        return merged

    def lazy_load_section(self, name, loader):
        """
        Register a loader callable under 'name' to load on first get().
        """
        self._loaders[name] = loader

    def get(self, name):
        """
        Retrieve a section, calling its loader if registered and not yet loaded.
        """
        if name in self.config:
            return self.config[name]
        if name in self._loaders:
            data = self._loaders[name]()
            self.config[name] = data
            return data
        return None

    def set_validation_context(self, context):
        """
        Set the current validation context: 'lab' or 'field'.
        """
        self.validation_context = context

    def validate(self):
        """
        Validate self.config based on the set context.
        """
        if self.validation_context == 'lab':
            ml = self.config.get('memory_limit')
            # require at least 512 for lab
            if ml is None or ml < 512:
                raise ValueError("Insufficient memory_limit for lab context")
        elif self.validation_context == 'field':
            net = self.config.get('network')
            if (not isinstance(net, dict) or
                not net.get('ssid') or
                not net.get('password')):
                raise ValueError("Missing network credentials for field context")
        # no-op for other contexts

    def load_config(self, path):
        """
        Load a JSON or INI config file.
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.json':
            with open(path, 'r') as fp:
                data = json.load(fp)
            if isinstance(data, dict):
                self.config = data.copy()
            else:
                self.config = data
            return self.config
        elif ext == '.ini':
            parser = configparser.ConfigParser()
            parser.read(path)
            result = {}
            for sect in parser.sections():
                result[sect] = dict(parser.items(sect))
            self.config = result
            return self.config
        else:
            raise ValueError(f"Unsupported config file extension '{ext}'")

    def load_env_file(self, path):
        """
        Load environment variables from a .env-style file.
        """
        self.env_vars = {}
        with open(path, 'r') as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    os.environ[key] = val
                    self.env_vars[key] = val
        return self.env_vars

    def register_plugin(self, plugin):
        """
        Register a plugin callable to be run in sequence.
        """
        self.plugins.append(plugin)

    def run_plugins(self, data):
        """
        Run all registered plugins over the data.
        """
        result = data
        for plugin in self.plugins:
            result = plugin(result)
        return result

    def apply_defaults(self):
        """
        Fill in default config values where missing.
        """
        defaults = {
            'timeout': 30,
            'sampling_interval': 60,
            'memory_limit': 1024
        }
        for key, val in defaults.items():
            if key not in self.config:
                self.config[key] = val

    def compose_schemas(self, schemas):
        """
        Compose a list of schemas by deep-merging them in order.
        """
        acc = {}
        for schema in schemas:
            acc = self.inherit_schema(acc, schema)
        # update the manager's config
        self.config.update(acc)
        return acc

    def expand_env_vars(self):
        """
        Recursively expand environment variables in all string values.
        """
        def _expand(value):
            if isinstance(value, str):
                return os.path.expandvars(value)
            if isinstance(value, list):
                return [_expand(v) for v in value]
            if isinstance(value, dict):
                return {k: _expand(v) for k, v in value.items()}
            return value

        self.config = _expand(self.config)

    def prompt_for_missing(self):
        """
        Prompt user for missing network ssid/password fields.
        """
        net = self.config.get('network')
        if not isinstance(net, dict):
            net = {}
        if not net.get('ssid'):
            ssid = input("Enter network ssid: ")
            net['ssid'] = ssid
        if not net.get('password'):
            pwd = input("Enter network password: ")
            net['password'] = pwd
        self.config['network'] = net
