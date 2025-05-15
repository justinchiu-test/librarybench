import os
import subprocess

def run_test(command, locale):
    """
    Run an external command under a given locale and capture stdout.
    Returns decoded stdout string.
    """
    env = os.environ.copy()
    env['LC_ALL'] = locale
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, _ = proc.communicate()
    return out.decode('utf-8')
