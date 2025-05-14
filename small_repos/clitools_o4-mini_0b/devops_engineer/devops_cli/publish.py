import subprocess

def publish_package(dist_dir="dist", repository_url=None):
    cmd = ["twine", "upload", f"{dist_dir}/*"]
    if repository_url:
        cmd += ["--repository-url", repository_url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
