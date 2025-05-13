"""
Package initialization and publishing for Security Analyst CLI.
"""
import os
import adapters.security_analyst.toml as toml

def init_package(target_dir, name, deps):
    os.makedirs(target_dir, exist_ok=True)
    # Create pyproject.toml with nested tables
    data = {'tool': {'poetry': {'name': name, 'dependencies': deps}}}
    content = toml.dumps(data)
    path = os.path.join(target_dir, 'pyproject.toml')
    with open(path, 'w') as f:
        f.write(content)
    return path

def publish_package(wheels, repo_url):
    # wheels: list of paths
    # Ensure each wheel has a corresponding .asc signature
    for w in wheels:
        sig = f"{w}.asc"
        if not os.path.exists(sig):
            raise ValueError(f"Missing signature for {w}")
    if not wheels or not repo_url:
        return False
    return True