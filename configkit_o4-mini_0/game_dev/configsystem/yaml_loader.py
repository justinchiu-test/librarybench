import yaml

class YAMLLoader:
    @staticmethod
    def load(file_path):
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        return data
