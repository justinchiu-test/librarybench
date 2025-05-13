import subprocess

def run_in_sandbox(cmd, timeout=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout, result.stderr, result.returncode
