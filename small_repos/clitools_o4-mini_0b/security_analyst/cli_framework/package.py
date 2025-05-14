import os
import toml
import subprocess

def init_package(path, project_name, dependencies):
    """
    Create pyproject.toml at path.
    dependencies: dict of name->version
    """
    data = {
        "tool": {
            "poetry": {
                "name": project_name,
                "version": "0.1.0",
                "description": "",
                "dependencies": dependencies,
                "dev-dependencies": {"flake8": "^3.8.4", "bandit": "^1.7.0"}
            }
        }
    }
    content = toml.dumps(data)
    full_path = os.path.join(path, "pyproject.toml")
    with open(full_path, "w") as f:
        f.write(content)
    return full_path

def publish_package(wheel_paths, repository_url, gpg_key=None):
    """
    Publish signed wheel files to repository.
    """
    for wheel in wheel_paths:
        asc = wheel + ".asc"
        if not os.path.exists(asc):
            raise ValueError(f"Missing signature for {wheel}")
        # GPG verify
        cmd = ["gpg", "--verify", asc, wheel]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise ValueError(f"GPG verification failed for {wheel}")
        # Simulate upload
    return True
