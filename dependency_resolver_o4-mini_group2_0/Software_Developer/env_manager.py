import os
from Software_Developer.utils import (
    load_json, dump_json, ensure_dir, remove_file, list_json_files
)

class EnvironmentManager:
    def __init__(self, base_dir="envs"):
        self.base_dir = base_dir
        ensure_dir(self.base_dir)

    def import_env(self, config_path):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"No such config file: {config_path}")
        data = load_json(config_path)
        name = data.get("name")
        if not name:
            raise ValueError("Environment config must have a 'name' field")
        dest = os.path.join(self.base_dir, f"{name}.json")
        dump_json(data, dest)
        return name

    def delete_env(self, name):
        path = os.path.join(self.base_dir, f"{name}.json")
        remove_file(path, f"Environment '{name}' does not exist")

    def list_envs(self):
        return list_json_files(self.base_dir)

    def get_env(self, name):
        path = os.path.join(self.base_dir, f"{name}.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist")
        return load_json(path)
