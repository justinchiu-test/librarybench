"""
Project scaffolding for data scientists.
"""
import os

def gen_scaffold(target_dir, project_name):
    # create project directory if not exists
    os.makedirs(target_dir, exist_ok=True)
    # create pyproject.toml with project name
    pyproject = os.path.join(target_dir, 'pyproject.toml')
    with open(pyproject, 'w', encoding='utf-8') as f:
        f.write(f'name = "{project_name}"')
    # create test_config.yaml
    cfg = os.path.join(target_dir, 'test_config.yaml')
    with open(cfg, 'w', encoding='utf-8') as f:
        f.write('# configuration\n')
    return target_dir