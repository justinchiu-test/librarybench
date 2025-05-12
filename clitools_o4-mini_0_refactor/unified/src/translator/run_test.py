"""
Run external commands for translator tests.
"""
import subprocess
import os

def run_test(cmd_args, locale=None):
    # Prepare environment
    env = os.environ.copy()
    if locale:
        env['LANG'] = locale
    # Execute command and capture output
    result = subprocess.run(cmd_args, capture_output=True, text=True, env=env)
    return result.stdout