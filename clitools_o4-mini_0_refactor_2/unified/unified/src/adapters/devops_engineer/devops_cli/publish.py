"""
Publish packages for DevOps Engineer CLI.
"""
import subprocess

def publish_package(dist_path, repo_url=None):
    cmd = ['twine', 'upload']
    if repo_url:
        cmd += ['--repository-url', repo_url]
    cmd.append(dist_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0