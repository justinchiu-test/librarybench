"""
Run external test command for Translator CLI adapter.
"""
import subprocess

def run_test(cmd, locale=None):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout