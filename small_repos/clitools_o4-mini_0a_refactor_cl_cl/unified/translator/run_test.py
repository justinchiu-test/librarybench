"""
Test runner for translator CLI tools.
"""

import os
import subprocess
from typing import List, Dict, Any, Optional


def run_test(command: List[str], locale: str = "en_US") -> str:
    """
    Run a test command with the specified locale.
    
    Args:
        command (List[str]): Command to run.
        locale (str): Locale to use.
        
    Returns:
        str: Command output.
    """
    # Set up environment with the specified locale
    env = os.environ.copy()
    env["LC_ALL"] = locale
    env["LANG"] = locale
    
    # Run the command
    try:
        result = subprocess.run(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Return stdout or stderr if there was an error
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    
    except Exception as e:
        return str(e)