import os
import json

class EnvironmentManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.environ.get(
            "ENV_MANAGER_HOME",
            os.path.expanduser("~/.envmanager")
        )
        self.envs_dir = os.path.join(self.base_dir, "envs")
        os.makedirs(self.envs_dir, exist_ok=True)

    def create_environment(self, name, packages):
        """Create a new environment with given package constraints."""
        path = os.path.join(self.envs_dir, f"{name}.json")
        if os.path.exists(path):
            raise FileExistsError(f"Environment '{name}' already exists.")
        with open(path, "w") as f:
            json.dump(packages, f, indent=2)
        return path

    def import_environment(self, file_path):
        """Import an environment config JSON file."""
        name = os.path.splitext(os.path.basename(file_path))[0]
        dest = os.path.join(self.envs_dir, f"{name}.json")
        if os.path.exists(dest):
            raise FileExistsError(f"Environment '{name}' already exists.")
        with open(file_path) as f:
            data = json.load(f)
        with open(dest, "w") as f:
            json.dump(data, f, indent=2)
        return name

    def delete_environment(self, name):
        """Delete an existing environment."""
        path = os.path.join(self.envs_dir, f"{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist.")
        os.remove(path)

    def list_environments(self):
        """List all available environments."""
        envs = []
        for fname in os.listdir(self.envs_dir):
            if fname.endswith(".json"):
                envs.append(os.path.splitext(fname)[0])
        return envs

    def get_environment(self, name):
        """Retrieve the package constraints of an environment."""
        path = os.path.join(self.envs_dir, f"{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Environment '{name}' does not exist.")
        with open(path) as f:
            return json.load(f)
