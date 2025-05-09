import os
import json
import shutil

class EnvironmentManager:
    def __init__(self, base_dir="envs"):
        self.base_dir = base_dir
        if not os.path.isdir(self.base_dir):
            os.makedirs(self.base_dir)

    def import_env(self, config_path):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"No such config file: {config_path}")
        with open(config_path, "r") as f:
            data = json.load(f)
        name = data.get("name")
        if not name:
            raise ValueError("Environment config must have a 'name' field")
        dest = os.path.join(self.base_dir, f"{name}.json")
        with open(dest, "w") as f:
            json.dump(data, f, indent=2)
        return name

    def delete_env(self, name):
        path = os.path.join(self.base_dir, f"{name}.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist")
        os.remove(path)

    def list_envs(self):
        files = os.listdir(self.base_dir)
        envs = [os.path.splitext(f)[0] for f in files if f.endswith(".json")]
        return sorted(envs)

    def get_env(self, name):
        path = os.path.join(self.base_dir, f"{name}.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist")
        with open(path) as f:
            return json.load(f)
