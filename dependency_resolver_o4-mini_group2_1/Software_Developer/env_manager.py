import os
from utils import load_json, save_json, ensure_dir, json_file_path

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
        dest = json_file_path(self.base_dir, name)
        save_json(dest, data)
        return name

    def delete_env(self, name):
        path = json_file_path(self.base_dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist")
        os.remove(path)

    def list_envs(self):
        files = os.listdir(self.base_dir)
        return sorted(os.path.splitext(f)[0]
                      for f in files if f.endswith(".json"))

    def get_env(self, name):
        path = json_file_path(self.base_dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist")
        return load_json(path)
