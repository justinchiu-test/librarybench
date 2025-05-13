"""
Scaffold generation for data_scientist datapipeline CLI.
"""
import os

def gen_scaffold(path, name):
    os.makedirs(path, exist_ok=True)
    py = os.path.join(path, 'pyproject.toml')
    with open(py, 'w') as f:
        f.write(f'name = "{name}"')
    cfg = os.path.join(path, 'test_config.yaml')
    with open(cfg, 'w') as f:
        f.write('')
    return path