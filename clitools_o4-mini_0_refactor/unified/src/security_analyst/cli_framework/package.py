"""
Project initialization and publishing for security analysts.
"""
import os
import subprocess
import security_analyst.toml as toml

def init_package(path, project_name, dependencies):
    # create directory
    os.makedirs(path, exist_ok=True)
    pyproject = os.path.join(path, 'pyproject.toml')
    data = {
        'tool': {
            'poetry': {
                'name': project_name,
                'version': '0.1.0',
                'dependencies': dependencies,
            }
        }
    }
    with open(pyproject, 'w', encoding='utf-8') as f:
        toml.dump(data, f)
    return pyproject

def publish_package(wheel_paths, repo_url):
    # wheel_paths: list of wheel file paths
    for wheel in wheel_paths:
        if not os.path.exists(wheel):
            raise ValueError(f"Wheel not found: {wheel}")
        sig = wheel + '.asc'
        if not os.path.exists(sig):
            raise ValueError(f"Signature not found: {sig}")
    # simulate upload
    cmd = ['publish', '--repo', repo_url] + wheel_paths
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0