import os

def gen_scaffold(path, project_name):
    base = os.path.join(path, project_name)
    os.makedirs(base, exist_ok=True)
    # Create pyproject.toml
    pyproject = os.path.join(base, 'pyproject.toml')
    with open(pyproject, 'w') as f:
        f.write(f'[tool.poetry]\nname = "{project_name}"\nversion = "0.1.0"\n')
    # Create sample test config
    cfg = os.path.join(base, 'test_config.yaml')
    with open(cfg, 'w') as f:
        f.write('sample_key: sample_value\n')
    return base
