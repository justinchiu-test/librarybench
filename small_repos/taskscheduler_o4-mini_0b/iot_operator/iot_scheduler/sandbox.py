import subprocess

def run_in_sandbox(script_path, cpu_limit=None, memory_limit=None, timeout=None):
    try:
        result = subprocess.run(['python', script_path], capture_output=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, b'', b''
